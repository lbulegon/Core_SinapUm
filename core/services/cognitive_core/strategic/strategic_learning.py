"""
Calibração a partir de StrategyFeedbackRecord: ajusta elasticidade e viés de impacto.
"""
from __future__ import annotations

from typing import Any, Dict, List, Tuple

def get_tenant_calibration(tenant_id: str, *, limit: int = 40) -> Dict[str, float]:
    """
    Lê feedbacks recentes; se previsões sistematicamente erradas, devolve multiplicadores.
    """
    out: Dict[str, float] = {
        "elasticity_scale": 1.0,
        "impact_bias": 0.0,
        "confidence_scale": 1.0,
    }
    try:
        from app_inbound_events.models import StrategyFeedbackRecord

        qs = (
            StrategyFeedbackRecord.objects.filter(tenant_id=str(tenant_id)[:64])
            .order_by("-created_at")[:limit]
        )
        rows: List[Tuple[float, float]] = []
        for r in qs:
            if r.realized_impact is None:
                continue
            rows.append((float(r.predicted_impact or 0), float(r.realized_impact)))
        if len(rows) < 5:
            return out
        variances = [b - a for a, b in rows]
        avg_var = sum(variances) / len(variances)
        # previsão alta demais → reduzir elasticidade efetiva (menos otimismo em demanda)
        if avg_var > 0.08:
            out["elasticity_scale"] = max(0.75, min(1.0, 1.0 - avg_var))
            out["impact_bias"] = -0.05 * min(1.0, avg_var * 3)
        elif avg_var < -0.08:
            out["elasticity_scale"] = min(1.12, 1.0 - avg_var * 0.3)
            out["impact_bias"] = 0.03
        # confiança: variância alta nas realizações
        import statistics

        try:
            st = statistics.stdev([b for _, b in rows])
            out["confidence_scale"] = max(0.7, min(1.0, 1.0 - st * 0.4))
        except statistics.StatisticsError:
            pass
    except Exception:
        pass
    return out


def apply_calibration_to_elasticity(base_elasticity: float, calibration: Dict[str, float]) -> float:
    e = float(base_elasticity) * float(calibration.get("elasticity_scale", 1.0))
    return max(-1.5, min(-0.15, e))
