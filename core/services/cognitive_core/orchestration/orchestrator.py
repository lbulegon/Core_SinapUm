"""
Orquestração: perception → reality → mediation → ação (efeitos colaterais explícitos).
"""
from __future__ import annotations

import logging
import os
import time
from typing import Dict, List, Optional

from app_inbound_events.models import InboundEvent
from core.services.cognitive_core.context.cognitive_context import CognitiveContext
from core.services.cognitive_core.mediation.decision_engine import DecisionEngine
from core.services.cognitive_core.memory.unified_memory import UnifiedCognitiveMemory
from core.services.cognitive_core.orchestration.cognitive_logging import PipelineTimer, log_pipeline_event
from core.services.cognitive_core.perception.adapters import perception_from_inbound_event
from core.services.cognitive_core.reality.builder import RealityStateBuilder
from core.services.whatsapp_gateway_service.client import WhatsAppGatewayClient, WhatsAppGatewayError

logger = logging.getLogger(__name__)


def _default_rag_namespaces() -> List[str]:
    raw = os.getenv("COGNITIVE_CORE_RAG_NAMESPACES", "global").strip()
    if not raw:
        return ["global"]
    return [x.strip() for x in raw.split(",") if x.strip()]


class CognitiveOrchestrator:
    def __init__(self) -> None:
        self.memory = UnifiedCognitiveMemory()
        self.engine = DecisionEngine()
        self.reality_builder = RealityStateBuilder(default_namespaces=_default_rag_namespaces())

    def run_inbound_whatsapp_flow(self, inbound_event_id: str) -> None:
        """
        Substitui o corpo cognitivo de `run_event_flow` mantendo efeitos externos idênticos.
        """
        started = time.time()
        ev = InboundEvent.objects.get(event_id=inbound_event_id)
        payload = ev.payload_json or {}
        text = payload.get("text") or payload.get("message") or ""
        user_id = payload.get("user_id") or payload.get("from") or ""

        perception = perception_from_inbound_event(ev, trace_id=inbound_event_id)
        log_pipeline_event(
            inbound_event_id,
            "perception",
            payload={"source": perception.source, "text_len": len(perception.text or "")},
        )
        ctx = CognitiveContext.from_perception(
            perception,
            extra={"rag_namespaces": _default_rag_namespaces()},
        )
        t_reality = PipelineTimer(inbound_event_id, "reality")
        reality = self.reality_builder.build(perception, ctx)
        t_reality.stop(
            rag_hits=len(reality.rag_long_term),
            live_keys=list((reality.operational_live or {}).keys())[:12],
            bottleneck=(reality.dynamic_metrics or {}).get("bottleneck_hint"),
        )

        t_dec = PipelineTimer(inbound_event_id, "decision")
        dec, policy, merged_ctx, cache_hit, response_text = self.engine.decide_inbound_whatsapp(
            event_id=inbound_event_id,
            perception=perception,
            reality=reality,
            ctx=ctx,
        )
        t_dec.stop(action=dec.action, risk=dec.risk_level, cache_hit=cache_hit)

        contract_version = perception.contract_version

        logger.info(
            "cognitive_trace %s stage=policy_decide route=%s allow_ai=%s",
            inbound_event_id,
            policy.route,
            policy.allow_ai,
        )
        logger.info(
            "cognitive_trace %s stage=decision action=%s cache_hit=%s risk=%s",
            inbound_event_id,
            dec.action,
            cache_hit,
            dec.risk_level,
        )

        send_ok = False
        send_error: Optional[str] = None
        try:
            gw = WhatsAppGatewayClient()
            gw_resp = gw.send_message(
                to=user_id,
                text=response_text,
                meta={
                    "event_id": inbound_event_id,
                    "route": policy.route,
                    "policy_version": policy.policy_version,
                    "contract_version": contract_version,
                    "cache_hit": cache_hit,
                    "cognitive_action": dec.action,
                    "trace_id": inbound_event_id,
                },
            )
            send_ok = True
            log_pipeline_event(
                inbound_event_id,
                "outcome",
                payload={"send_ok": True, "route": policy.route},
            )
            logger.info("cognitive_trace %s stage=send_message_ok gateway=%s", inbound_event_id, gw_resp)
        except WhatsAppGatewayError as e:
            send_error = str(e)
            logger.warning("cognitive_trace %s stage=send_message_failed error=%s", inbound_event_id, send_error)
            raise
        finally:
            self.memory.record_decision_trace(
                trace_id=inbound_event_id,
                perception_source=perception.source,
                contexto={
                    "perception": {
                        "source": perception.source,
                        "text_preview": (text[:500] if text else ""),
                    },
                    "reality": {
                        "rag_hits": len(reality.rag_long_term),
                        "namespaces": reality.rag_namespaces,
                        "graph_stub": bool(reality.graph_structural.get("stub")),
                    },
                    "mediation": dec.to_dict(),
                    "llm_context_keys": list(merged_ctx.keys()) if merged_ctx else [],
                },
                decisao={
                    "route": policy.route,
                    "allow_ai": policy.allow_ai,
                    "policy_version": policy.policy_version,
                    "template_id": policy.template_id,
                    "tags": policy.tags or [],
                    "decision_action": dec.action,
                    "confidence": dec.confidence,
                },
                resultado={
                    "cache_hit": cache_hit,
                    "send_ok": send_ok,
                    "send_error": send_error or None,
                    "elapsed_s": round(time.time() - started, 3),
                    "risk_level": dec.risk_level,
                    "expected_outcome_preview": (dec.expected_outcome or "")[:400],
                },
                source="cognitive_core_orchestrator",
            )

        self.engine.evora_client.domain_append_message(
            event_id=inbound_event_id,
            direction="outbound",
            message_text=response_text,
            metadata={
                "route": policy.route,
                "cache_hit": cache_hit,
                "tags": policy.tags or [],
                "template_id": policy.template_id,
                "policy_version": policy.policy_version,
                "contract_version": contract_version,
                "cognitive_action": dec.action,
            },
            contract_version=contract_version,
        )
        logger.info(
            "cognitive_trace %s stage=done elapsed=%s",
            inbound_event_id,
            round(time.time() - started, 3),
        )
