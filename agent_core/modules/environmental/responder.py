from __future__ import annotations

from typing import Any

from agent_core.core.interfaces import Responder


class EnvironmentalResponder(Responder):
    """R — ações declarativas (alertas / recomendações) para consumo upstream."""

    def __init__(self, module_options: dict[str, Any] | None = None) -> None:
        self._module_options = module_options or {}

    def handle(self, decision: str, context: dict[str, Any]) -> dict[str, Any] | None:
        if decision == "ENV_CRITICAL":
            return {
                "module": "environmental",
                "type": "alert",
                "message": "Sobrecarga crítica detectada no ambiente operacional",
            }
        if decision == "ENV_PRESSURE":
            return {
                "module": "environmental",
                "type": "action",
                "message": "Reduzir carga operacional e priorizar fluxos leves",
            }
        return None
