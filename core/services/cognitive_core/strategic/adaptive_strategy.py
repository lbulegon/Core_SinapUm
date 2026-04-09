"""
Peso adaptativo da estratégia a partir de StrategyFeedbackRecord (variance previsto vs realizado).
"""
from __future__ import annotations

import logging
from typing import Any, Dict

logger = logging.getLogger(__name__)


def adjust_strategy_weights(tenant_id: str, *, limit: int = 120) -> Dict[str, Any]:
    """
    Compara feedbacks com baixa vs alta variância para inclinar conservadorismo ou agressividade.
    """
    tid = str(tenant_id or "").strip()[:64]
    if not tid:
        return {
            "agressividade": 0,
            "conservadorismo": 0,
            "net": 0,
            "samples": 0,
        }
    try:
        from app_inbound_events.models import StrategyFeedbackRecord

        qs = list(
            StrategyFeedbackRecord.objects.filter(tenant_id=tid).order_by("-created_at")[:limit]
        )
    except Exception as e:
        logger.debug("adjust_strategy_weights: %s", e)
        return {
            "agressividade": 0,
            "conservadorismo": 0,
            "net": 0,
            "samples": 0,
        }

    sucesso = [f for f in qs if f.variance is not None and float(f.variance) < 0.2]
    falha = [f for f in qs if f.variance is not None and float(f.variance) > 0.5]
    return {
        "agressividade": len(sucesso),
        "conservadorismo": len(falha),
        "net": len(sucesso) - len(falha),
        "samples": len(sucesso) + len(falha),
    }


def merge_adaptive_weights_into_objective(
    objective_profile: Dict[str, Any],
    adaptive: Dict[str, Any],
) -> Dict[str, Any]:
    """
    Se conservadorismo > agressividade, aumenta MINIMIZE_DELAY e reduz um pouco MAXIMIZE_PROFIT; caso contrário o inverso leve.
    """
    from core.services.cognitive_core.strategic.strategy_objective import (
        BALANCE_LOAD,
        MAXIMIZE_PROFIT,
        MINIMIZE_DELAY,
        ObjectiveFunction,
    )

    out = dict(objective_profile or {})
    cons = int(adaptive.get("conservadorismo") or 0)
    agr = int(adaptive.get("agressividade") or 0)
    w = dict(out.get("weights") or ObjectiveFunction.default_weights())
    if cons > agr:
        w[MINIMIZE_DELAY] = float(w.get(MINIMIZE_DELAY, 0.35)) + 0.08
        w[MAXIMIZE_PROFIT] = max(0.12, float(w.get(MAXIMIZE_PROFIT, 0.45)) - 0.06)
        w[BALANCE_LOAD] = float(w.get(BALANCE_LOAD, 0.20))
    elif agr > cons:
        w[MAXIMIZE_PROFIT] = float(w.get(MAXIMIZE_PROFIT, 0.45)) + 0.06
        w[MINIMIZE_DELAY] = max(0.18, float(w.get(MINIMIZE_DELAY, 0.35)) - 0.04)
        w[BALANCE_LOAD] = float(w.get(BALANCE_LOAD, 0.20))
    s = sum(max(0.0, float(v)) for v in w.values())
    if s > 0:
        w = {k: float(v) / s for k, v in w.items()}
    out["weights"] = w
    out["adaptive_tilt"] = "conservative" if cons > agr else ("aggressive" if agr > cons else "neutral")
    return out
