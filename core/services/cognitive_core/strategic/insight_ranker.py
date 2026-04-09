"""
Priorização de insights para autonomia: alinhamento com StrategicContext (intenção).
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from core.services.cognitive_core.autonomy.autonomy_logging import log_autonomy
from core.services.cognitive_core.insights.insight_engine import Insight
from core.services.cognitive_core.strategic.strategic_context import (
    OBJECTIVE_INCREASE_MARGIN,
    OBJECTIVE_MAINTAIN_STABILITY,
    OBJECTIVE_MAX_THROUGHPUT,
    OBJECTIVE_REDUCE_DELAY,
    StrategicContext,
)


@dataclass
class RankedInsight:
    insight: Insight
    strategic_score: float
    alignment: Dict[str, float] = field(default_factory=dict)
    notes: str = ""


class StrategyEvaluator:
    """
    Avalia e ordena insights segundo objetivos estratégicos (sem LLM).
    """

    # pattern_key -> (contribuição por objetivo 0–1)
    _PATTERN_OBJECTIVE_VECTORS: Dict[str, Dict[str, float]] = {
        "feedback_recurring_delay": {
            OBJECTIVE_REDUCE_DELAY: 0.95,
            OBJECTIVE_MAX_THROUGHPUT: 0.55,
            OBJECTIVE_MAINTAIN_STABILITY: 0.35,
            OBJECTIVE_INCREASE_MARGIN: 0.15,
        },
        "operational_bottleneck_kitchen": {
            OBJECTIVE_REDUCE_DELAY: 0.9,
            OBJECTIVE_MAX_THROUGHPUT: 0.85,
            OBJECTIVE_MAINTAIN_STABILITY: 0.25,
            OBJECTIVE_INCREASE_MARGIN: 0.1,
        },
        "operational_high_load": {
            OBJECTIVE_REDUCE_DELAY: 0.65,
            OBJECTIVE_MAX_THROUGHPUT: 0.7,
            OBJECTIVE_MAINTAIN_STABILITY: 0.5,
            OBJECTIVE_INCREASE_MARGIN: 0.2,
        },
        "operational_throughput_drop": {
            OBJECTIVE_MAX_THROUGHPUT: 0.95,
            OBJECTIVE_REDUCE_DELAY: 0.45,
            OBJECTIVE_INCREASE_MARGIN: 0.35,
            OBJECTIVE_MAINTAIN_STABILITY: 0.3,
        },
        "feedback_success_streak": {
            OBJECTIVE_MAINTAIN_STABILITY: 0.9,
            OBJECTIVE_INCREASE_MARGIN: 0.4,
            OBJECTIVE_MAX_THROUGHPUT: 0.3,
            OBJECTIVE_REDUCE_DELAY: 0.1,
        },
        "anomaly_low_decision_score": {
            OBJECTIVE_MAINTAIN_STABILITY: 0.75,
            OBJECTIVE_INCREASE_MARGIN: 0.25,
            OBJECTIVE_REDUCE_DELAY: 0.35,
            OBJECTIVE_MAX_THROUGHPUT: 0.25,
        },
    }

    @classmethod
    def rank_insights(
        cls,
        insights: List[Insight],
        strategic_context: StrategicContext,
        *,
        dynamic_metrics: Optional[Dict[str, Any]] = None,
    ) -> List[RankedInsight]:
        """
        Ordena por score estratégico decrescente.
        `dynamic_metrics` reforça relevância (ex.: carga alta aumenta peso de throughput).
        """
        dm = dynamic_metrics or {}
        load_boost = 1.0 + 0.15 * min(1.0, float(dm.get("estimated_load") or 0))

        ranked: List[RankedInsight] = []
        for ins in insights:
            vec = dict(cls._PATTERN_OBJECTIVE_VECTORS.get(ins.pattern_key, {}))
            if not vec:
                vec = {
                    OBJECTIVE_REDUCE_DELAY: 0.4,
                    OBJECTIVE_MAX_THROUGHPUT: 0.4,
                    OBJECTIVE_MAINTAIN_STABILITY: 0.4,
                    OBJECTIVE_INCREASE_MARGIN: 0.2,
                }
            alignment: Dict[str, float] = {}
            score = 0.0
            wsum = 0.0
            for obj in strategic_context.objetivos:
                w = strategic_context.weight_for(obj)
                if w <= 0:
                    continue
                a = float(vec.get(obj, 0.25))
                alignment[obj] = round(a, 3)
                score += w * a
                wsum += w
            if wsum > 0:
                score /= wsum
            score *= ins.confidence * (0.85 + 0.15 * ins.estimated_impact)
            if ins.pattern_key in ("operational_high_load", "operational_bottleneck_kitchen"):
                score *= load_boost

            ri = RankedInsight(
                insight=ins,
                strategic_score=round(min(1.0, score), 4),
                alignment=alignment,
                notes="ranked_by_strategic_context",
            )
            ranked.append(ri)
            log_autonomy(
                "insight_scored",
                tenant_id=ins.tenant_id,
                payload={
                    "insight_id": ins.insight_id,
                    "pattern": ins.pattern_key,
                    "strategic_score": ri.strategic_score,
                    "objetivos": strategic_context.objetivos,
                },
            )

        ranked.sort(key=lambda r: r.strategic_score, reverse=True)
        return ranked
