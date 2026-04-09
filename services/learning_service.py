"""
Agregação de padrões a partir de `SinapCoreLog` — taxa de sucesso por decisão.

Uso típico: relatórios no EOC e priorização de handlers.
"""

from __future__ import annotations

from typing import Any


class LearningService:
    """Extrai estatísticas de auditoria sem acoplar ao PAOR."""

    @staticmethod
    def extract_patterns(limit: int = 1000) -> dict[str, dict[str, Any]]:
        from app_sinapcore.models.sinapcore_log import SinapCoreLog

        logs = list(SinapCoreLog.objects.order_by("-timestamp")[:limit])
        patterns: dict[str, dict[str, Any]] = {}

        for log in logs:
            key = log.decision or "(sem decisão)"
            if key not in patterns:
                patterns[key] = {"count": 0, "success": 0}
            patterns[key]["count"] += 1
            if log.action == "executed":
                patterns[key]["success"] += 1

        for k, v in patterns.items():
            c = v["count"]
            v["success_rate"] = (v["success"] / c) if c else 0.0

        return patterns
