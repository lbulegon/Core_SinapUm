from __future__ import annotations

from typing import Any

from agent_core.core.interfaces import Analyzer


class EnvironmentalAnalyzer(Analyzer):
    """Interpreta snapshot ambiental → severidade + metadados para orquestração."""

    def __init__(self, module_options: dict[str, Any] | None = None) -> None:
        self._module_options = module_options or {}

    def analyze(self, perception: dict[str, Any]) -> dict[str, Any]:
        if perception.get("module") != "environmental":
            return {"module": "environmental", "severity": "low", "state": None, "score": None}

        raw = perception.get("data") or {}
        state = raw.get("state")
        score = raw.get("score")

        if state == "colapso":
            severity = "critical"
        elif state == "sobrecarga":
            severity = "high"
        elif state == "pressao":
            severity = "medium"
        else:
            severity = "low"

        action = {
            "colapso": "intervir_imediatamente",
            "sobrecarga": "reduzir_pressao",
            "pressao": "monitorar",
        }.get(state, "normal")

        return {
            "module": "environmental",
            "severity": severity,
            "score": score,
            "state": state,
            "action": action,
        }
