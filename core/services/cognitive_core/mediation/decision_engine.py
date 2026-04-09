"""
DecisionEngine — único lugar nomeado 'decisão' mediadora.
EOC = enrich apenas. LLM = interpretante, chamado só quando a decisão assim o determina.
"""
from __future__ import annotations

import json
import logging
from typing import Any, Dict, Optional, Tuple

from django.conf import settings

from app_mcp.clients.evora_mcp_client import EvoraMCPClient, PolicyDecision
from core.services.cognitive.eoc import eoc_enrich_bundle
from core.services.cognitive_core.behavior_profile.chef_agno_profile import ChefAgnoProfile
from core.services.cognitive_core.context.cognitive_context import CognitiveContext
from core.services.cognitive_core.mediation.acoes_operacionais import AcoesOperacionais
from core.services.cognitive_core.prediction.delay_predictor import predict_delay_risk
from core.services.cognitive_core.rag.rag_learning import get_action_performance
from core.services.cognitive_core.mediation.decision_output import DecisionOutput
from core.services.cognitive_core.perception.input import PerceptionInput
from core.services.cognitive_core.reality.state import RealityState
from core.services.llm_gateway_service.gateway import llm_generate
from core.services.semantic_cache_service.cache import semantic_query, semantic_store

logger = logging.getLogger(__name__)


def _impacto_rag_max_escala() -> int:
    return max(1, int(getattr(settings, "SINAPUM_IMPACTO_RAG_MAX_ESCALA", 12)))


def _previsao_atraso_threshold() -> int:
    return int(getattr(settings, "SINAPUM_PREVISAO_ATRASO_THRESHOLD", 14))


class DecisionEngine:
    """
    Terceiridade: combina policy (Evora), enrich (EOC), estado real (RealityState) e regras explícitas.
    """

    def __init__(self, evora: Optional[EvoraMCPClient] = None):
        self._evora = evora or EvoraMCPClient()

    @property
    def evora_client(self) -> EvoraMCPClient:
        return self._evora

    def decide_inbound_whatsapp(
        self,
        *,
        event_id: str,
        perception: PerceptionInput,
        reality: RealityState,
        ctx: CognitiveContext,
    ) -> Tuple[DecisionOutput, PolicyDecision, Dict[str, Any], bool, str]:
        """
        Fluxo equivalente ao legado run_event_flow (decisão + execução de resposta).

        Returns:
            decision_output, policy_decision, merged_llm_context, cache_hit, response_text
        """
        text = perception.text
        channel = perception.channel or perception.source
        user_id = perception.user_id
        contract_version = perception.contract_version
        policy_hint = perception.context_hint()

        policy = self._evora.policy_decide(
            event_id=event_id,
            channel=channel,
            user_id=user_id,
            text=text,
            context_hint=policy_hint,
            contract_version=contract_version,
        )

        cache_context: Dict[str, Any] = {
            "route": policy.route,
            "tags": policy.tags or [],
            "template_id": policy.template_id,
            "user_id": user_id,
            "channel": channel,
        }

        cached = semantic_query(intent=text, context=cache_context)
        if cached is not None:
            out = DecisionOutput(
                action="respond_from_semantic_cache",
                confidence=0.95,
                reasoning=["Cache semântico hit; não reexecutar RAG/LLM."],
                metadata={"route": policy.route, "policy_version": policy.policy_version},
                response_text=cached,
                use_llm_interpretant=False,
                expected_outcome="Resposta reproduzida do cache semântico (baixa variância).",
                risk_level="low",
            )
            ctx.add_event("decision", out.to_dict())
            return out, policy, {}, True, cached

        # Enrich (EOC) — não é decisão
        enrich_input: Dict[str, Any] = {
            "text": text,
            "context_hint": {
                **policy_hint,
                **reality.operational,
                "operational_live": reality.operational_live,
                "dynamic_metrics": reality.dynamic_metrics,
                "reality_rag_count": len(reality.rag_long_term),
            },
            "k": 5,
            "precomputed_rag": reality.rag_long_term,
        }
        enrich = eoc_enrich_bundle(enrich_input)
        rag = enrich.get("rag") or []
        riscos = enrich.get("riscos") or {}
        hints = enrich.get("hints") or {}

        merged_llm_context: Dict[str, Any] = {
            "route": policy.route,
            "tags": policy.tags or [],
            "template_id": policy.template_id,
            "user_id": user_id,
            "channel": channel,
            "rag_results": rag,
            "riscos_previstos": riscos,
            "user_text": text,
            "reality_slice": reality.to_llm_context_slice(),
            "eoc_hints": hints,
            "cognitive_version": "cognitive_core_v1",
        }

        r_score = float(riscos.get("score") or 0)
        risk_lvl = ChefAgnoProfile.risk_level_from_score(r_score)
        exp_txt = ChefAgnoProfile.expected_outcome_text(
            action="inbound_whatsapp",
            hints=hints,
            riscos=riscos,
            reality=reality,
        )
        reasoning: list[str] = [
            f"Policy route={policy.route} allow_ai={policy.allow_ai}",
            f"RAG hits={len(rag)} risco_score={riscos.get('score')}",
        ]

        if policy.allow_ai:
            response_text = llm_generate(
                prompt_input=text,
                context=merged_llm_context,
                prompt_version=policy.prompt_version or "v1",
                contract_version=contract_version,
            )
            semantic_store(
                intent=text,
                context=cache_context,
                response=response_text,
                ttl_seconds=policy.ttl_seconds,
            )
            base_c = max(0.0, min(1.0, 1.0 - r_score * 0.15))
            conf = ChefAgnoProfile.adjust_confidence(base_c, reality=reality, risco_score=r_score)
            out = DecisionOutput(
                action="generate_with_llm_interpretant",
                confidence=conf,
                reasoning=reasoning + ["LLM usado como interpretante sob decisão explícita allow_ai."],
                metadata={
                    "route": policy.route,
                    "policy_version": policy.policy_version,
                    "prompt_version": policy.prompt_version,
                },
                response_text=response_text,
                use_llm_interpretant=True,
                expected_outcome=exp_txt,
                risk_level=risk_lvl,
            )
        else:
            response_text = policy.template_text or "Certo — vou encaminhar isso para atendimento."
            semantic_store(
                intent=text,
                context=cache_context,
                response=response_text,
                ttl_seconds=policy.ttl_seconds,
            )
            out = DecisionOutput(
                action="respond_template",
                confidence=ChefAgnoProfile.adjust_confidence(0.85, reality=reality, risco_score=r_score),
                reasoning=reasoning + ["Policy negou LLM; resposta por template/policy."],
                metadata={"route": policy.route, "policy_version": policy.policy_version},
                response_text=response_text,
                use_llm_interpretant=False,
                expected_outcome=exp_txt,
                risk_level=risk_lvl,
            )

        ctx.add_event("decision", out.to_dict())
        return out, policy, merged_llm_context, False, response_text

    def decide_orbital_support(
        self,
        *,
        perception: PerceptionInput,
        reality: RealityState,
        ctx: CognitiveContext,
    ) -> DecisionOutput:
        """
        MrFoo / orbitais: sem Evora policy; enrich + regras → suporte à execução local.
        """
        text = perception.text
        enrich_input = {
            "text": text or "mrfoo:context",
            "context_hint": {
                **perception.context_hint(),
                **reality.operational,
                "operational_live": reality.operational_live,
                "dynamic_metrics": reality.dynamic_metrics,
            },
            "k": int(perception.raw_data.get("k", 5) or 5),
            "precomputed_rag": reality.rag_long_term,
        }
        enrich = eoc_enrich_bundle(enrich_input)
        hints = enrich.get("hints") or {}
        riscos = enrich.get("riscos") or {}
        r_score = float(riscos.get("score") or 0)
        risk_lvl = ChefAgnoProfile.risk_level_from_score(r_score)

        reasoning = [
            "Orbital path: sem policy Evora; apenas enrich + heurísticas.",
            f"risco_score={riscos.get('score')}",
        ]
        action = "orbital_hints_only"
        if hints.get("prioridade_delta"):
            action = "orbital_bump_priority_suggested"
        if hints.get("atencao_cliente"):
            action = "orbital_customer_attention_suggested"

        impacto_rag = int((reality.operational_live or {}).get("impacto_rag") or 0)
        max_imp = _impacto_rag_max_escala()
        impacto_norm = round(min(1.0, float(impacto_rag) / float(max_imp)), 4)
        ol_pre = reality.operational_live or {}
        snap_pre = ol_pre.get("client_operational_snapshot") or ol_pre.get("operational_snapshot") or {}
        tamanho_fila = int(snap_pre.get("pedidos_ativos_count") or 0) if isinstance(snap_pre, dict) else 0
        tid_orbital = str(perception.context_hint().get("tenant_id") or "").strip()
        tempo_signal = 0.0
        if isinstance(snap_pre, dict):
            tempo_signal = max(
                float(snap_pre.get("atraso_medio_segundos") or 0),
                float(snap_pre.get("tempo_medio_preparo_segundos") or 0),
            )
        nivel_atraso, risco_prev, taxa_hist = predict_delay_risk(
            tid_orbital, impacto_rag, tamanho_fila, tempo_signal
        )
        previsao_score = int(impacto_rag) + tamanho_fila
        previsao_th = _previsao_atraso_threshold()
        heuristica_atraso = previsao_score > previsao_th
        modelo_atraso = nivel_atraso in ("alto", "medio")
        metadata: Dict[str, Any] = {
            "hints": hints,
            "rag_count": len(enrich.get("rag") or []),
            "trace_id": ctx.trace_id,
            "bottleneck": (reality.dynamic_metrics or {}).get("bottleneck_hint"),
            "impacto_rag": impacto_rag,
            "impacto_rag_max_escala": max_imp,
            "impacto_rag_normalizado": impacto_norm,
            "rag_impacto_resumo": (reality.operational_live or {}).get("rag_impacto_resumo"),
            "rag_context_n": len(reality.rag_context or []),
            "tamanho_fila_snapshot": tamanho_fila,
            "previsao_atraso_score": previsao_score,
            "previsao_atraso_nivel": nivel_atraso,
            "previsao_atraso_risco": risco_prev,
            "taxa_atraso_historico": taxa_hist,
            "previsao_atraso": heuristica_atraso or modelo_atraso,
        }
        # RAG híbrido → variável operacional (escada de ações)
        if impacto_rag >= 4:
            action = "orbital_reduzir_complexidade_suggested"
            metadata["acao"] = AcoesOperacionais.REDUZIR_COMPLEXIDADE
            metadata["rag_influencia"] = True
            metadata["motivo"] = (
                "Impacto RAG acumulado elevado (≥4) — reduzir complexidade de preparo ou alternativas."
            )
            reasoning.append(f"impacto_rag={impacto_rag} ≥ 4 → acao=reduzir_complexidade")
        elif impacto_rag >= 2:
            action = "orbital_monitorar_preparo_suggested"
            metadata["acao"] = AcoesOperacionais.MONITORAR_PREPARO
            metadata["rag_influencia"] = True
            metadata["motivo"] = "Impacto RAG moderado (≥2) — reforçar atenção ao preparo e à fila."
            reasoning.append(f"impacto_rag={impacto_rag} ≥ 2 → acao=monitorar_preparo")

        if metadata.get("previsao_atraso"):
            reasoning.append(
                f"previsao_atraso: heuristica={heuristica_atraso} nivel={nivel_atraso} risco={risco_prev} "
                f"score_fila={metadata.get('previsao_atraso_score')} th={previsao_th}"
            )

        acao_meta = metadata.get("acao")
        if tid_orbital and acao_meta:
            lw_acao = get_action_performance(tid_orbital, str(acao_meta))
            metadata["learning_weight_acao"] = round(lw_acao, 4)
            if lw_acao < 0.8:
                metadata["alerta_aprendizado"] = "acao_com_baixa_performance"
                reasoning.append(
                    f"learning_weight_acao={lw_acao:.3f} < 0.8 → alerta_aprendizado"
                )

        base_c = max(0.0, min(1.0, 0.5 + r_score * 0.5))
        conf = ChefAgnoProfile.adjust_confidence(base_c, reality=reality, risco_score=r_score)
        exp_txt = ChefAgnoProfile.expected_outcome_text(
            action=action, hints=hints, riscos=riscos, reality=reality
        )

        out = DecisionOutput(
            action=action,
            confidence=conf,
            reasoning=reasoning,
            metadata=metadata,
            response_text=None,
            use_llm_interpretant=False,
            expected_outcome=exp_txt,
            risk_level=risk_lvl,
        )
        try:
            ol = reality.operational_live or {}
            logger.info(
                "decision_support_rag %s",
                json.dumps(
                    {
                        "rag_used": bool(reality.rag_long_term),
                        "rag_sources": list(ol.get("rag_sources_distinct") or []),
                        "impacto_rag": ol.get("impacto_rag"),
                        "impacto_rag_normalizado": metadata.get("impacto_rag_normalizado"),
                        "acao": metadata.get("acao"),
                        "rag_influencia": metadata.get("rag_influencia"),
                        "rag_context_n": metadata.get("rag_context_n"),
                        "previsao_atraso": metadata.get("previsao_atraso"),
                        "previsao_atraso_nivel": metadata.get("previsao_atraso_nivel"),
                        "previsao_atraso_risco": metadata.get("previsao_atraso_risco"),
                        "previsao_atraso_score": metadata.get("previsao_atraso_score"),
                        "learning_weight_acao": metadata.get("learning_weight_acao"),
                        "alerta_aprendizado": metadata.get("alerta_aprendizado"),
                    },
                    ensure_ascii=False,
                ),
            )
        except Exception:
            logger.debug("decision_support_rag log falhou", exc_info=True)
        ctx.add_event("orbital_decision", out.to_dict())
        return out

    def decide_strategic_support(
        self,
        *,
        perception: PerceptionInput,
        reality: RealityState,
        ctx: CognitiveContext,
        strategy_proposal: Optional[Dict[str, Any]] = None,
    ) -> DecisionOutput:
        """
        Fase 4: estratégia → mesmo pipeline orbital (EOC + hints), com metadados de estratégia.
        Não substitui decide_orbital_support; apenas marca e injeta contexto para auditoria.
        """
        sp = strategy_proposal or {}
        merged = dict(perception.raw_data or {})
        ch = dict(perception.context_hint() or {})
        ch["strategic"] = True
        ch["strategy_proposal"] = sp
        merged["context_hint"] = ch
        norm = dict(perception.normalized_data or {})
        norm["context_hint"] = ch
        perception2 = PerceptionInput(
            source=perception.source,
            raw_data=merged,
            normalized_data=norm,
            timestamp=perception.timestamp,
            trace_id=perception.trace_id,
            metadata={**perception.metadata, "strategic": True},
        )
        out = self.decide_orbital_support(perception=perception2, reality=reality, ctx=ctx)
        out.metadata = {
            **(out.metadata or {}),
            "strategic": True,
            "strategy_proposal_id": sp.get("proposal_id"),
            "strategy_tipo": sp.get("tipo"),
        }
        out.cognitive_version = "cognitive_core_v4_strategic"
        ctx.add_event("strategic_decision", out.to_dict())
        return out
