"""
Valida propostas estratégicas contra RealityState (capacidade, carga, gargalos).
"""
from __future__ import annotations

from typing import Any, Dict, List, Tuple

from core.services.cognitive_core.reality.state import RealityState
from core.services.cognitive_core.strategic.strategy_models import StrategyProposal


def validate_against_reality(
    proposal: StrategyProposal,
    reality: RealityState,
) -> Tuple[bool, List[str]]:
    """
    Bloqueia estratégias que agravariam colapso operacional evidente.
    """
    reasons: List[str] = []
    dm = reality.dynamic_metrics or {}
    ol = reality.operational_live or {}
    load = float(dm.get("estimated_load") or 0)
    bottleneck = dm.get("bottleneck_hint") or ol.get("gargalo_hint")

    if proposal.tipo == "expansao" and load > 0.85:
        reasons.append("carga operacional alta — expansão arriscada")

    if proposal.tipo == "preco" and proposal.risco == "high" and load > 0.75:
        reasons.append("risco alto de preço sob carga elevada")

    if proposal.tipo == "operacao" and bottleneck and "cozinha" in str(bottleneck) and proposal.prioridade == "critical":
        reasons.append("gargalo na cozinha — priorizar desbloqueio antes de mudança crítica")

    if proposal.tipo == "cardapio" and load > 0.9 and "remove" not in str(proposal.parametros):
        reasons.append("carga muito alta — simplificar cardápio apenas com remoções seguras")

    return (len(reasons) == 0, reasons)


def merge_reality_capacity_hint(reality: RealityState) -> Dict[str, Any]:
    """Trecho para contexto de decisão estratégica."""
    return {
        "estimated_load": (reality.dynamic_metrics or {}).get("estimated_load"),
        "bottleneck": (reality.dynamic_metrics or {}).get("bottleneck_hint"),
        "rag_hits": len(reality.rag_long_term or []),
    }
