from __future__ import annotations

from typing import Any

from agent_core.core.interfaces import Orchestrator


class EnvironmentalOrchestrator(Orchestrator):
    """Converte análises ambientais em códigos de decisão (ENV_*)."""

    def __init__(self, module_options: dict[str, Any] | None = None) -> None:
        self._module_options = module_options or {}

    def decide(self, analyses: list[dict[str, Any]]) -> str | None:
        for a in analyses:
            if a.get("module") != "environmental":
                continue
            if a.get("severity") == "critical":
                return "ENV_CRITICAL"
            if a.get("severity") == "high":
                return "ENV_PRESSURE"
        return None
