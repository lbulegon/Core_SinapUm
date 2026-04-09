from __future__ import annotations

from typing import Any

from agent_core.core.interfaces import Perceptor


class EnvironmentalPerceptor(Perceptor):
    """Lê estado Redis `env_state:{id}` — fonte P do módulo ambiental."""

    def __init__(self, module_options: dict[str, Any] | None = None) -> None:
        self._module_options = module_options or {}

    def perceive(self, context: dict[str, Any]) -> dict[str, Any] | None:
        from services.environmental_state_service import EnvironmentalStateService

        estabelecimento_id = context.get("estabelecimento_id")
        if estabelecimento_id is None:
            return None

        state = EnvironmentalStateService.get_state(estabelecimento_id)
        if not state:
            return None

        return {
            "module": "environmental",
            "type": "environmental_state",
            "data": state,
        }
