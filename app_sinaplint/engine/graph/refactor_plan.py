"""
Plano executivo de refactor: prioridade qualitativa + ações sugeridas por app.
"""

from __future__ import annotations

from typing import Any


class RefactorPlanGenerator:
    def generate(self, priorities: list[dict[str, Any]]) -> list[dict[str, Any]]:
        plan: list[dict[str, Any]] = []
        for item in priorities:
            actions: list[str] = []
            if int(item.get("in_cycles") or 0) > 0:
                actions.append("Quebrar dependência circular (SCC)")
            if item.get("high_coupling"):
                actions.append("Reduzir acoplamento (interfaces / services)")
            if int(item.get("fan_in") or 0) > 5:
                actions.append("Dividir módulo dominante (God App)")
            if int(item.get("dependencies") or 0) > 5:
                actions.append("Revisar dependências externas entre apps")

            plan.append(
                {
                    "app": item.get("app"),
                    "impact_score": int(item.get("impact_score") or 0),
                    "priority": self._classify(int(item.get("impact_score") or 0)),
                    "actions": actions,
                }
            )
        return plan

    def _classify(self, score: int) -> str:
        if score > 80:
            return "critical"
        if score > 50:
            return "high"
        if score > 20:
            return "medium"
        return "low"
