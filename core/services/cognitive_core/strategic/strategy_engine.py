"""
StrategyEngine — KPIs + padrões + realidade → propostas estratégicas + simulação opcional.
Toda proposta deve passar depois por DecisionEngine (decide_strategic_support).
"""
from __future__ import annotations

import hashlib
from typing import Any, Dict, List, Optional, Tuple

from core.services.cognitive_core.patterns.pattern_engine import PatternMatch
from core.services.cognitive_core.reality.state import RealityState
from core.services.cognitive_core.strategic.adaptive_strategy import (
    adjust_strategy_weights,
    merge_adaptive_weights_into_objective,
)
from core.services.cognitive_core.strategic.kpi_engine import compute_kpi_bundle
from core.services.cognitive_core.strategic.menu_optimizer import menu_suggestions_from_kpi
from core.services.cognitive_core.strategic.strategic_learning import apply_calibration_to_elasticity, get_tenant_calibration
from core.services.cognitive_core.strategic.strategy_evaluator import validate_against_reality
from core.services.cognitive_core.strategic.strategy_models import KPIBundle, ProductKPI, StrategyProposal
from core.services.cognitive_core.strategic.strategy_selector import StrategySelector
from core.services.cognitive_core.strategic.strategy_simulator import (
    simulation_to_dict,
    simulate_menu_remove,
    simulate_systemic_price_focus,
)


class StrategyEngine:
    def __init__(self) -> None:
        pass

    def build_proposals(
        self,
        *,
        kpi: KPIBundle,
        pattern_matches: Optional[List[PatternMatch]] = None,
        tenant_id: str = "",
    ) -> List[StrategyProposal]:
        proposals: List[StrategyProposal] = []
        pattern_matches = pattern_matches or []

        # Produtos de baixo lucro/hora
        worst = sorted(kpi.por_produto, key=lambda p: p.lucro_por_hora_prep)[:5]
        best = kpi.por_produto[:5] if kpi.por_produto else []

        for p in worst:
            if p.margem_pct < 15 and p.receita > 0:
                pid = self._pid("remove", p.item_id, tenant_id)
                proposals.append(
                    StrategyProposal(
                        proposal_id=pid,
                        tipo="cardapio",
                        titulo=f"Reavaliar remoção ou reestruturação: {p.nome}",
                        descricao="Margem baixa e lucro/hora de preparo fraco.",
                        impacto_estimado=0.55,
                        risco="medium",
                        prioridade="normal",
                        parametros={"item_id": p.item_id, "acao": "remove_or_reprice"},
                    )
                )

        # Competição entre preços no item (sistémico depois no run)
        for p in worst[:2]:
            if p.margem_pct < 15 and p.receita > 0:
                for delta in (3.0, 5.0):
                    proposals.append(
                        StrategyProposal(
                            proposal_id=self._pid(f"pi{int(delta)}", p.item_id, tenant_id),
                            tipo="preco",
                            titulo=f"Simular +{int(delta)}% preço: {p.nome}",
                            descricao="Item com margem baixa — cenário de reajuste pontual (com spillover).",
                            impacto_estimado=0.48,
                            risco="medium",
                            prioridade="normal",
                            parametros={
                                "item_id": p.item_id,
                                "delta_pct": delta,
                                "scope": "item",
                            },
                        )
                    )

        for p in best[:3]:
            pid = self._pid("prioritize", p.item_id, tenant_id)
            proposals.append(
                StrategyProposal(
                    proposal_id=pid,
                    tipo="operacao",
                    titulo=f"Priorizar produção / marketing: {p.nome}",
                    descricao="Alto score de margem e lucro por tempo de preparo.",
                    impacto_estimado=0.62,
                    risco="low",
                    prioridade="high",
                    parametros={"item_id": p.item_id, "acao": "prioritize_production"},
                )
            )

        # Padrões de atraso → preço ou operação
        keys = {m.pattern_key for m in pattern_matches}
        if "feedback_recurring_delay" in keys or "operational_bottleneck_kitchen" in keys:
            proposals.append(
                StrategyProposal(
                    proposal_id=self._pid("delay", "global", tenant_id),
                    tipo="operacao",
                    titulo="Reduzir fila antes de subir preços",
                    descricao="Atraso ou gargalo recorrente — foco em throughput antes de pricing.",
                    impacto_estimado=0.7,
                    risco="medium",
                    prioridade="high",
                    parametros={"acao": "throughput_first"},
                )
            )

        if kpi.margem_media_pct < 20 and kpi.economic.receita > 0:
            for delta in (3.0, 5.0, 7.0):
                proposals.append(
                    StrategyProposal(
                        proposal_id=self._pid(f"pg{int(delta)}", "global", tenant_id),
                        tipo="preco",
                        titulo=f"Simular +{int(delta)}% preço médio (agregado)",
                        descricao="Margem agregada baixa; competição entre deltas antes de aplicar.",
                        impacto_estimado=0.42 + 0.02 * (delta / 7.0),
                        risco="medium",
                        prioridade="normal",
                        parametros={"delta_pct": delta, "scope": "global"},
                    )
                )

        # dedupe por titulo
        seen = set()
        unique: List[StrategyProposal] = []
        for pr in proposals:
            if pr.titulo in seen:
                continue
            seen.add(pr.titulo)
            unique.append(pr)
        return unique[:20]

    def filter_feasible(
        self,
        proposals: List[StrategyProposal],
        reality: RealityState,
    ) -> List[StrategyProposal]:
        """Remove invalidadas por RealityState."""
        out: List[StrategyProposal] = []
        for p in proposals:
            ok, _ = validate_against_reality(p, reality)
            if ok:
                out.append(p)
        return out

    def _pid(self, kind: str, ref: str, tenant: str) -> str:
        h = hashlib.sha256(f"{kind}:{ref}:{tenant}".encode()).hexdigest()[:12]
        return f"str_{h}"


def _operational_proxy_simulation(proposal: StrategyProposal, kpi: KPIBundle) -> Dict[str, Any]:
    acao = str(proposal.parametros.get("acao") or "")
    mm = kpi.margem_media_pct
    m_ratio = mm / 100.0 if mm > 1 else mm
    base: Dict[str, Any] = {
        "cenario": "operacao_proxy",
        "systemic": False,
        "receita_antes": round(kpi.economic.receita, 2),
        "receita_depois": round(kpi.economic.receita, 2),
        "margem_antes": round(m_ratio, 4),
        "margem_depois": round(m_ratio, 4),
    }
    if "throughput" in acao:
        base["fila_alivio_pct"] = 12.0
        base["lucro_total_delta_pct"] = 2.5
        base["spillover_stress"] = 0.02
    elif "prioritize" in acao:
        base["fila_alivio_pct"] = 4.0
        base["lucro_total_delta_pct"] = 1.2
        base["spillover_stress"] = 0.03
    else:
        base["fila_alivio_pct"] = 5.0
        base["lucro_total_delta_pct"] = 0.8
        base["spillover_stress"] = 0.05
    return base


def _simulate_for_proposal(
    proposal: StrategyProposal,
    *,
    kpi: KPIBundle,
    calibration: Dict[str, float],
) -> Dict[str, Any]:
    base_e = -0.6
    elast = apply_calibration_to_elasticity(base_e, calibration)
    rt = max(1e-6, float(kpi.economic.receita))

    if proposal.tipo == "preco":
        delta = float(proposal.parametros.get("delta_pct") or proposal.parametros.get("delta") or 5.0)
        scope = str(proposal.parametros.get("scope") or "global")
        if scope == "item" and proposal.parametros.get("item_id"):
            iid = str(proposal.parametros["item_id"])
            row = next((p for p in kpi.por_produto if p.item_id == iid), None)
            if row:
                share = max(0.02, min(0.95, float(row.receita) / rt))
                return simulate_systemic_price_focus(
                    receita_total=rt,
                    item_revenue_share=share,
                    margem_pct_base=row.margem_pct,
                    price_delta_pct=delta,
                    demand_elasticity=elast,
                )
        return simulate_systemic_price_focus(
            receita_total=rt,
            item_revenue_share=1.0,
            margem_pct_base=kpi.margem_media_pct,
            price_delta_pct=delta,
            demand_elasticity=elast,
        )

    if proposal.tipo == "cardapio":
        iid = str(proposal.parametros.get("item_id") or "")
        row: Optional[ProductKPI] = next((p for p in kpi.por_produto if p.item_id == iid), None)
        if row and row.receita > 0:
            sim = simulate_menu_remove(
                receita_total=rt,
                receita_item=float(row.receita),
                margem_pct=row.margem_pct,
            )
            d = simulation_to_dict(sim)
            l0 = float(sim.receita_antes) * float(sim.margem_antes)
            l1 = float(sim.receita_depois) * float(sim.margem_depois)
            d["lucro_total_delta_pct"] = round(((l1 - l0) / l0 * 100.0) if l0 > 0 else 0.0, 3)
            ta = float(sim.tempo_producao_horas_antes) or 1.0
            td = float(sim.tempo_producao_horas_depois) or ta
            d["fila_alivio_pct"] = round(max(0.0, min(25.0, (1.0 - td / ta) * 20.0)) if ta > 0 else 0.0, 3)
            d["systemic"] = True
            d["spillover_stress"] = round(min(1.0, 0.04 + 0.12 * (float(row.receita) / rt)), 4)
            return d
        return {
            "cenario": "cardapio_sem_item",
            "systemic": False,
            "fila_alivio_pct": 2.0,
            "lucro_total_delta_pct": 0.0,
            "spillover_stress": 0.06,
        }

    return _operational_proxy_simulation(proposal, kpi)


def _operational_load_from_reality(reality: RealityState, economic_payload: Dict[str, Any]) -> float:
    dm = reality.dynamic_metrics or {}
    if isinstance(dm.get("estimated_load"), (int, float)):
        return max(0.0, min(1.0, float(dm["estimated_load"])))
    op = economic_payload.get("operational")
    if isinstance(op, dict):
        inner = op.get("dynamic_metrics")
        if isinstance(inner, dict) and isinstance(inner.get("estimated_load"), (int, float)):
            return max(0.0, min(1.0, float(inner["estimated_load"])))
    return 0.0


def run_strategic_analysis(
    *,
    tenant_id: str,
    economic_payload: Dict[str, Any],
    reality: RealityState,
    pattern_matches: Optional[List[PatternMatch]] = None,
    objective_profile: Optional[Dict[str, Any]] = None,
    strategy_top_k: Optional[int] = None,
) -> Dict[str, Any]:
    """
    Pipeline completo: KPIBundle → propostas → filtro realidade → simulação → função objetivo → ranking.
    economic_payload: { product_rows, economic, operational } — típico do MrFoo.
    """
    kpi = compute_kpi_bundle(
        economic_input=economic_payload.get("economic"),
        product_rows=economic_payload.get("product_rows") or economic_payload.get("items"),
        operational=economic_payload.get("operational"),
    )
    menu_optimizer_hints = menu_suggestions_from_kpi(kpi)
    adaptive_w = adjust_strategy_weights(tenant_id)
    obj_profile = merge_adaptive_weights_into_objective(dict(objective_profile or {}), adaptive_w)
    se = StrategyEngine()
    props = se.build_proposals(kpi=kpi, pattern_matches=pattern_matches, tenant_id=tenant_id)
    feasible = se.filter_feasible(props, reality)
    calibration = get_tenant_calibration(tenant_id)
    load = _operational_load_from_reality(reality, economic_payload)

    candidates: List[Tuple[StrategyProposal, Dict[str, Any]]] = [
        (p, _simulate_for_proposal(p, kpi=kpi, calibration=calibration)) for p in feasible
    ]

    n = len(candidates)
    ranked_full = StrategySelector.select_best(
        candidates,
        objective_profile=obj_profile,
        kpi=kpi,
        operational_load=load,
        top_k=max(1, n) if n else 1,
    )
    if strategy_top_k is not None:
        lim = max(1, min(n, int(strategy_top_k))) if n else 0
        ranked_slice = ranked_full[:lim]
    else:
        ranked_slice = ranked_full

    proposals_out: List[Dict[str, Any]] = []
    for i, ss in enumerate(ranked_slice, start=1):
        p = ss.proposal
        proposals_out.append(
            {
                "rank": i,
                "objective_score": ss.score,
                "simulation": ss.simulation,
                "proposal_id": p.proposal_id,
                "tipo": p.tipo,
                "titulo": p.titulo,
                "descricao": p.descricao,
                "impacto_estimado": p.impacto_estimado,
                "risco": p.risco,
                "prioridade": p.prioridade,
                "parametros": p.parametros,
            }
        )

    return {
        "tenant_id": tenant_id,
        "kpi": {
            "margem_media_pct": kpi.margem_media_pct,
            "lucro_hora_operacao": kpi.lucro_hora_operacao,
            "throughput_financeiro_h": kpi.throughput_financeiro_h,
            "custo_atraso_estimado": kpi.custo_atraso_estimado,
            "eficiencia_operacional": kpi.eficiencia_operacional,
            "economic": {
                "receita": kpi.economic.receita,
                "custo": kpi.economic.custo,
                "margem_pct": kpi.economic.margem_pct(),
            },
            "top_produtos": [
                {
                    "item_id": p.item_id,
                    "nome": p.nome,
                    "margem_pct": p.margem_pct,
                    "lucro_por_hora_prep": p.lucro_por_hora_prep,
                    "score": p.score,
                }
                for p in kpi.por_produto[:15]
            ],
        },
        "strategy_selection": {
            "candidates_count": len(candidates),
            "returned_count": len(proposals_out),
            "strategy_top_k": strategy_top_k,
            "operational_load": load,
            "objective_profile": obj_profile,
            "adaptive_strategy": adaptive_w,
            "tenant_calibration": {
                "elasticity_scale": calibration.get("elasticity_scale"),
                "impact_bias": calibration.get("impact_bias"),
                "confidence_scale": calibration.get("confidence_scale"),
            },
        },
        "menu_optimizer": menu_optimizer_hints,
        "proposals": proposals_out,
        "proposals_rejected_count": len(props) - len(feasible),
        "proposals_raw_count": len(props),
    }

