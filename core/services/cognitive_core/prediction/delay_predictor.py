"""
Risco de atraso iminente: combina histórico (DecisionFeedbackRecord) com fila, RAG e tempo médio.
"""
from __future__ import annotations

import logging
from typing import Any, Dict, Tuple

logger = logging.getLogger(__name__)


def _outcome_indicates_delay(outcome_json: Dict[str, Any]) -> bool:
    if not isinstance(outcome_json, dict):
        return False
    if outcome_json.get("atraso") is True:
        return True
    rr = str(outcome_json.get("resultado_real") or "").strip().lower()
    if rr == "atraso":
        return True
    return False


def _historical_delay_rate(tenant_id: str, *, limit: int = 100) -> float:
    tid = str(tenant_id or "").strip()
    if not tid:
        return 0.0
    try:
        from app_inbound_events.models import DecisionFeedbackRecord

        qs = list(
            DecisionFeedbackRecord.objects.filter(tenant_id=tid[:64])
            .order_by("-created_at")[:limit]
        )
        if not qs:
            return 0.0
        delays = sum(1 for h in qs if _outcome_indicates_delay(h.outcome_json or {}))
        return float(delays) / float(len(qs))
    except Exception as e:
        logger.debug("predict_delay: histórico indisponível: %s", e)
        return 0.0


def predict_delay_risk(
    tenant_id: str,
    impacto_rag: int,
    fila: int,
    tempo_medio_segundos: float,
) -> Tuple[str, float, float]:
    """
    Devolve (nível, score_risco_0_1, taxa_atraso_hist_0_1).

    nível: \"alto\" | \"medio\" | \"baixo\"
    """
    taxa = _historical_delay_rate(tenant_id)
    i_norm = min(1.0, float(max(0, int(impacto_rag))) / 12.0)
    f_norm = min(1.0, float(max(0, int(fila))) / 35.0)
    # pressão temporal: 30 min de referência ≈ 1.0
    t_raw = max(0.0, float(tempo_medio_segundos or 0.0))
    t_norm = min(1.0, t_raw / 1800.0)
    score = (i_norm * 0.4) + (f_norm * 0.3) + (t_norm * 0.3)
    # histórico amplifica risco quando há padrão de atraso
    risco = min(1.0, score * (0.45 + 0.55 * taxa))

    if risco > 0.62:
        nivel = "alto"
    elif risco > 0.32:
        nivel = "medio"
    else:
        nivel = "baixo"

    return nivel, round(risco, 4), round(taxa, 4)
