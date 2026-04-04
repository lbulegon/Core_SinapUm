"""
Pesos de aprendizagem a partir de DecisionFeedbackRecord (decisão → resultado real).
"""
from __future__ import annotations

import logging
from typing import Optional

from django.db.models import Avg, Q

logger = logging.getLogger(__name__)


def get_action_performance(tenant_id: str, action: Optional[str]) -> float:
    """
    Média de `decision_score_posterior` para registros cuja ação RAG coincide com `action`.
    Sem dados ou action vazia → 1.0 (neutro).
    Retorno clampado ~[0.5, 1.5] para multiplicar score no ranker.
    """
    act = (action or "").strip()
    if not act or act == "default":
        return 1.0
    tid = str(tenant_id or "").strip()
    if not tid:
        return 1.0
    try:
        from app_inbound_events.models import DecisionFeedbackRecord

        qs = DecisionFeedbackRecord.objects.filter(tenant_id=tid).filter(
            Q(decision_json__metadata__acao=act) | Q(outcome_json__acao_rag=act)
        )
        row = qs.aggregate(avg=Avg("decision_score_posterior"))
        avg = row.get("avg")
        if avg is None:
            return 1.0
        w = 1.0 + float(avg) / 10.0
        return max(0.5, min(1.5, w))
    except Exception as e:
        logger.debug("get_action_performance: %s", e)
        return 1.0
