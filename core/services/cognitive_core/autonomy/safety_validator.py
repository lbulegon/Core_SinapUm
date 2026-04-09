"""
Guardrails obrigatórios antes de execução automática (nível 3).
LLM não valida — apenas regras sobre DecisionOutput + proposta.
"""
from __future__ import annotations

from typing import Dict, List, Tuple

from core.services.cognitive_core.actions.action_generator import ActionProposal
from core.services.cognitive_core.autonomy import autonomy_config
from core.services.cognitive_core.mediation.decision_output import DecisionOutput


# Tools consideradas de baixo risco para execução automática
_LOW_RISK_TOOLS = frozenset({"noop", "core.rag_query", "core.eoc_enrich"})


def validate_auto_execution(
    decision: DecisionOutput,
    proposal: ActionProposal,
) -> Tuple[bool, List[str]]:
    """
    Retorna (ok, razões). Execução só se ok.
    """
    reasons: List[str] = []
    min_conf = autonomy_config.get_min_confidence_for_auto()
    if decision.confidence < min_conf:
        reasons.append(f"confidence {decision.confidence:.2f} < {min_conf}")

    max_risk = autonomy_config.get_max_risk_for_auto()
    risk_order = {"low": 0, "medium": 1, "high": 2}
    if risk_order.get(decision.risk_level, 1) > risk_order.get(max_risk, 1):
        reasons.append(f"risk {decision.risk_level} exceeds max {max_risk}")

    tool = (proposal.mcp_tool or "").strip()
    if tool and tool not in _LOW_RISK_TOOLS:
        # decision_support pode mover prioridade — exige confiança extra
        if tool == "core.decision_support" and decision.confidence < max(min_conf, 0.78):
            reasons.append("decision_support requires higher confidence")

    if proposal.priority == "high" and decision.confidence < min_conf + 0.05:
        reasons.append("high priority proposal blocked: confidence margin")

    return (len(reasons) == 0, reasons)


def validate_context_minimum(
    *,
    tenant_id: str,
    operational_live: Dict[str, Any],
) -> Tuple[bool, List[str]]:
    """Evita autonomia sem tenant. Snapshot operacional é opcional (nível 2+ pode usar só feedback)."""
    reasons: List[str] = []
    if not str(tenant_id).strip():
        reasons.append("missing tenant_id")
    return (len(reasons) == 0, reasons)
