"""
Analisa DecisionFeedbackRecord + snapshots operacionais (operational_live / dynamic_metrics).
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import timedelta
from typing import Any, Dict, List, Optional

from django.utils import timezone

from core.services.cognitive_core.autonomy.autonomy_logging import log_autonomy


@dataclass
class PatternMatch:
    pattern_key: str
    tenant_id: str
    confidence: float
    signals: Dict[str, Any] = field(default_factory=dict)


class PatternEngine:
    """
    Detectores leves (regras). Extensível via novos métodos _detect_*.
    """

    def __init__(
        self,
        *,
        feedback_lookback_hours: int = 72,
        delay_rate_threshold: float = 0.45,
        success_streak_min: int = 5,
        load_threshold: float = 0.72,
        low_score_threshold: float = 0.42,
        throughput_drop_ratio: float = 0.65,
    ):
        self.feedback_lookback_hours = feedback_lookback_hours
        self.delay_rate_threshold = delay_rate_threshold
        self.success_streak_min = success_streak_min
        self.load_threshold = load_threshold
        self.low_score_threshold = low_score_threshold
        self.throughput_drop_ratio = throughput_drop_ratio

    def run(
        self,
        *,
        tenant_id: str,
        operational_live: Optional[Dict[str, Any]] = None,
        dynamic_metrics: Optional[Dict[str, Any]] = None,
    ) -> List[PatternMatch]:
        matches: List[PatternMatch] = []
        operational_live = operational_live or {}
        dynamic_metrics = dynamic_metrics or {}

        matches.extend(self._detect_feedback_patterns(tenant_id))
        matches.extend(
            self._detect_operational_patterns(
                tenant_id,
                operational_live,
                dynamic_metrics,
            )
        )

        for m in matches:
            log_autonomy(
                "pattern_detected",
                tenant_id=tenant_id,
                payload={"pattern": m.pattern_key, "confidence": m.confidence, "signals": m.signals},
            )
        return matches

    def _detect_feedback_patterns(self, tenant_id: str) -> List[PatternMatch]:
        out: List[PatternMatch] = []
        try:
            from app_inbound_events.models import DecisionFeedbackRecord
        except Exception:
            return out

        since = timezone.now() - timedelta(hours=self.feedback_lookback_hours)
        qs = (
            DecisionFeedbackRecord.objects.filter(tenant_id=str(tenant_id), created_at__gte=since)
            .order_by("-created_at")[:80]
        )
        rows = list(qs)
        if not rows:
            return out

        delay_hits = 0
        low_scores = 0
        scored = 0
        for r in rows:
            oj = r.outcome_json or {}
            if oj.get("atraso") or oj.get("delay"):
                delay_hits += 1
        streak = 0
        for r in rows:
            if r.was_effective is True:
                streak += 1
            else:
                break
        total = len(rows)
        delay_rate = delay_hits / max(1, total)

        if delay_rate >= self.delay_rate_threshold and total >= 6:
            out.append(
                PatternMatch(
                    "feedback_recurring_delay",
                    tenant_id,
                    confidence=min(1.0, delay_rate + 0.15),
                    signals={"delay_rate": delay_rate, "sample": total},
                )
            )

        if len(rows) >= self.success_streak_min and streak >= self.success_streak_min:
            out.append(
                PatternMatch(
                    "feedback_success_streak",
                    tenant_id,
                    confidence=0.78,
                    signals={"streak": streak},
                )
            )

        for r in rows[:30]:
            if r.decision_score_posterior is not None:
                scored += 1
                if float(r.decision_score_posterior) < self.low_score_threshold:
                    low_scores += 1
        if scored >= 8 and low_scores / scored >= 0.5:
            out.append(
                PatternMatch(
                    "anomaly_low_decision_score",
                    tenant_id,
                    confidence=min(1.0, low_scores / scored + 0.1),
                    signals={"low_ratio": low_scores / scored, "scored": scored},
                )
            )

        return out

    def _detect_operational_patterns(
        self,
        tenant_id: str,
        operational_live: Dict[str, Any],
        dynamic_metrics: Dict[str, Any],
    ) -> List[PatternMatch]:
        out: List[PatternMatch] = []
        load = float(dynamic_metrics.get("estimated_load") or 0)
        if load >= self.load_threshold:
            out.append(
                PatternMatch(
                    "operational_high_load",
                    tenant_id,
                    confidence=min(1.0, load + 0.05),
                    signals={"estimated_load": load},
                )
            )

        bh = dynamic_metrics.get("bottleneck_hint") or operational_live.get("gargalo_hint")
        snap = operational_live.get("client_operational_snapshot") or operational_live.get(
            "operational_snapshot"
        )
        if isinstance(snap, dict):
            bh = bh or snap.get("gargalo_hint")
        if bh in ("cozinha_em_preparo", "kitchen", "cozinha"):
            out.append(
                PatternMatch(
                    "operational_bottleneck_kitchen",
                    tenant_id,
                    confidence=0.82,
                    signals={"bottleneck_hint": bh},
                )
            )

        if isinstance(snap, dict):
            cur = snap.get("throughput_pedidos_por_hora_estimado")
            ref = snap.get("throughput_reference_por_hora")
            try:
                if cur is not None and ref is not None and float(ref) > 0:
                    ratio = float(cur) / float(ref)
                    if ratio < self.throughput_drop_ratio:
                        out.append(
                            PatternMatch(
                                "operational_throughput_drop",
                                tenant_id,
                                confidence=min(1.0, 1.0 - ratio),
                                signals={"ratio": ratio, "current": cur, "reference": ref},
                            )
                        )
            except (TypeError, ValueError):
                pass

        return out
