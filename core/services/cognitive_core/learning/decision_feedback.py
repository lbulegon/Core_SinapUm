"""
Loop de feedback: decisão prevista vs resultado operacional real (ORM + opcional vectorstore).
"""
from __future__ import annotations

import logging
import time
from typing import Any, Dict, Optional

from django.utils import timezone

from core.services.cognitive_core.behavior_profile.chef_agno_profile import ChefAgnoProfile

logger = logging.getLogger(__name__)


def score_feedback_vs_prediction(
    *,
    predicted_risk_level: str,
    outcome: Dict[str, Any],
) -> tuple[float, bool]:
    """Calcula decision_score posterior e se a decisão foi 'efetiva' no sentido operacional."""
    atraso = bool(outcome.get("atraso") or outcome.get("delay") or outcome.get("late"))
    erro = bool(outcome.get("erro") or outcome.get("error"))
    pred_high = predicted_risk_level == "high"
    return ChefAgnoProfile.score_decision_quality(
        outcome_atraso=atraso,
        predicted_risk_high=pred_high,
        erro_operacional=erro,
    )


def record_decision_feedback_event(
    *,
    trace_id: str,
    tenant_id: str,
    source: str,
    decision_action: str,
    decision_snapshot: Dict[str, Any],
    predicted: Dict[str, Any],
    outcome: Dict[str, Any],
    upsert_vectorstore: bool = False,
) -> Optional[str]:
    """
    Persiste DecisionFeedbackRecord e opcionalmente reforça memória semântica (vectorstore).
    Retorna id do registro ou None.
    """
    try:
        from app_inbound_events.models import DecisionFeedbackRecord
    except Exception as e:
        logger.warning("DecisionFeedbackRecord unavailable: %s", e)
        return None

    risk = str(predicted.get("risk_level") or "medium")
    score, effective = score_feedback_vs_prediction(predicted_risk_level=risk, outcome=outcome)

    row = DecisionFeedbackRecord.objects.create(
        trace_id=trace_id[:128],
        tenant_id=str(tenant_id)[:64],
        source=source[:64],
        decision_action=decision_action[:128],
        decision_json=decision_snapshot,
        predicted_json=predicted,
        outcome_json=outcome,
        was_effective=effective,
        impact_score=score - 0.5,
        decision_score_posterior=score,
        evaluated_at=timezone.now(),
    )

    if upsert_vectorstore:
        try:
            from core.services.learning.order_feedback_service import save_order_feedback

            save_order_feedback(
                {
                    "tenant_id": tenant_id,
                    "pedido_id": str(outcome.get("pedido_id") or trace_id)[:64],
                    "context": {"decision_feedback": True, "trace_id": trace_id},
                    "plan": predicted,
                    "outcome": outcome,
                    "success": effective,
                    "extra_tag": "decision_feedback_v2",
                }
            )
        except Exception as e:
            logger.debug("vectorstore upsert optional failed: %s", e)

    return str(row.id)


def build_predicted_payload(decision_dict: Dict[str, Any]) -> Dict[str, Any]:
    """Extrait campos previstos para comparação com outcome."""
    return {
        "risk_level": decision_dict.get("risk_level") or "medium",
        "expected_outcome": decision_dict.get("expected_outcome"),
        "confidence": decision_dict.get("confidence"),
        "action": decision_dict.get("action"),
        "cognitive_version": decision_dict.get("cognitive_version"),
        "ts": time.time(),
    }
