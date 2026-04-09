"""Persistência de StrategyFeedback (ORM)."""
from __future__ import annotations

from typing import Any, Dict, Optional


def record_strategy_feedback(
    *,
    tenant_id: str,
    strategy_key: str,
    proposal_id: str = "",
    predicted_impact: float = 0.0,
    realized_impact: Optional[float] = None,
    payload: Optional[Dict[str, Any]] = None,
) -> Optional[str]:
    try:
        from app_inbound_events.models import StrategyFeedbackRecord
    except Exception:
        return None
    var = None
    if realized_impact is not None:
        var = round(float(realized_impact) - float(predicted_impact), 4)
    row = StrategyFeedbackRecord.objects.create(
        tenant_id=str(tenant_id)[:64],
        strategy_key=strategy_key[:128],
        proposal_id=(proposal_id or "")[:128],
        predicted_impact=float(predicted_impact),
        realized_impact=realized_impact,
        variance=var,
        payload_json=payload or {},
    )
    return str(row.id)
