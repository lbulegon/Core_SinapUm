from __future__ import annotations

from typing import Any

from agent_core.modules.environmental.analyzer import EnvironmentalAnalyzer
from agent_core.modules.environmental.orchestrator import EnvironmentalOrchestrator
from agent_core.modules.environmental.perceptor import EnvironmentalPerceptor
from agent_core.modules.environmental.responder import EnvironmentalResponder
from agent_core.registry.module_registry import ModuleDescriptor


class EnvironmentalModule:
    """Módulo ambiental — instanciável com `config` vindo do Admin."""

    name = "environmental"

    def __init__(self, config: Any = None) -> None:
        self.config = config
        extra = self._module_options()
        self.perceptor = EnvironmentalPerceptor(module_options=extra)
        self.analyzer = EnvironmentalAnalyzer(module_options=extra)
        self.orchestrator = EnvironmentalOrchestrator(module_options=extra)
        self.responder = EnvironmentalResponder(module_options=extra)

    def _module_options(self) -> dict[str, Any] | None:
        if self.config is None:
            return None
        raw = self.config.config
        return raw if isinstance(raw, dict) else None

    def to_descriptor(self) -> ModuleDescriptor:
        pri = int(self.config.priority) if self.config is not None else 10
        return ModuleDescriptor(
            name=self.name,
            perceptor=self.perceptor,
            analyzer=self.analyzer,
            orchestrator=self.orchestrator,
            responder=self.responder,
            enabled=True,
            priority=pri,
        )

    @staticmethod
    def descriptor() -> ModuleDescriptor:
        return EnvironmentalModule(config=None).to_descriptor()
