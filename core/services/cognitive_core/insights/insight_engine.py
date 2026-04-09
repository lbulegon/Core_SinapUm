"""
Gera Insights a partir de PatternMatch — sem LLM (descrições são templates).
"""
from __future__ import annotations

from dataclasses import dataclass, field
import hashlib
from typing import Any, Dict, List, Optional

from core.services.cognitive_core.autonomy.autonomy_logging import log_autonomy
from core.services.cognitive_core.patterns.pattern_engine import PatternMatch


@dataclass
class Insight:
    insight_id: str
    kind: str  # risk | opportunity | anomaly
    description: str
    estimated_impact: float
    confidence: float
    tenant_id: str
    pattern_key: str
    metadata: Dict[str, Any] = field(default_factory=dict)


class InsightEngine:
    def from_patterns(self, matches: List[PatternMatch]) -> List[Insight]:
        out: List[Insight] = []
        for m in matches:
            ins = self._match_to_insight(m)
            if ins:
                out.append(ins)
                log_autonomy(
                    "insight_generated",
                    tenant_id=m.tenant_id,
                    payload={
                        "insight_id": ins.insight_id,
                        "kind": ins.kind,
                        "pattern": m.pattern_key,
                        "confidence": ins.confidence,
                    },
                )
        return out

    def _match_to_insight(self, m: PatternMatch) -> Optional[Insight]:
        kind_map = {
            "feedback_recurring_delay": ("risk", "Atrasos recorrentes nos feedbacks — risco de SLA."),
            "anomaly_low_decision_score": ("anomaly", "Scores posteriores baixos — qualidade de decisão em queda."),
            "feedback_success_streak": ("opportunity", "Decisões recentes eficazes — manter política atual."),
            "operational_high_load": ("risk", "Carga operacional elevada — risco de filas e erros."),
            "operational_bottleneck_kitchen": ("risk", "Gargalo na cozinha — preparo pode atrasar pedidos."),
            "operational_throughput_drop": ("anomaly", "Throughput abaixo do referencial — possível desaceleração."),
        }
        if m.pattern_key not in kind_map:
            return None
        kind, desc = kind_map[m.pattern_key]
        impact = min(1.0, 0.35 + m.confidence * 0.55)
        iid = hashlib.sha256(
            f"{m.tenant_id}:{m.pattern_key}:{m.signals}".encode("utf-8", errors="ignore")
        ).hexdigest()[:24]
        return Insight(
            insight_id=f"ins_{iid}",
            kind=kind,
            description=desc,
            estimated_impact=round(impact, 3),
            confidence=round(m.confidence, 3),
            tenant_id=m.tenant_id,
            pattern_key=m.pattern_key,
            metadata={"signals": m.signals},
        )
