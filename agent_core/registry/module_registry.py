from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Any, ClassVar, Type

from agent_core.core.interfaces import Analyzer, Orchestrator, Perceptor, Responder
from services.semantic_module_config import get_module_config

logger = logging.getLogger(__name__)


@dataclass
class ModuleDescriptor:
    """Módulo cognitivo plugável (perceptor + analyzer + orchestrator + responder)."""

    name: str
    perceptor: Perceptor
    analyzer: Analyzer
    orchestrator: Orchestrator
    responder: Responder
    enabled: bool = True
    priority: int = 0


class ModuleRegistry:
    """Registo de módulos; ativos resolvidos em services.module_registry_runtime."""

    _modules: ClassVar[list[ModuleDescriptor]] = []
    MODULE_MAP: ClassVar[dict[str, Type[Any]]] = {}

    @classmethod
    def _ensure_module_map(cls) -> None:
        if cls.MODULE_MAP:
            return
        from agent_core.modules.environmental.module import EnvironmentalModule

        cls.MODULE_MAP = {
            "environmental": EnvironmentalModule,
        }

    @classmethod
    def register(cls, module: ModuleDescriptor) -> None:
        for i, m in enumerate(cls._modules):
            if m.name == module.name:
                cls._modules[i] = module
                return
        cls._modules.append(module)

    @classmethod
    def clear(cls) -> None:
        cls._modules = []

    @classmethod
    def all_modules(cls) -> list[ModuleDescriptor]:
        return list(cls._modules)

    @classmethod
    def get_active_modules(cls) -> list[ModuleDescriptor]:
        from services.module_registry_runtime import resolve_active_modules

        return resolve_active_modules()

    @classmethod
    def _get_static_active_modules(cls) -> list[ModuleDescriptor]:
        cfg = get_module_config()
        active: list[ModuleDescriptor] = []
        for m in cls._modules:
            mc = cfg.get(m.name, {})
            enabled = mc.get("enabled", m.enabled)
            if not enabled:
                continue
            priority = int(mc.get("priority", m.priority))
            active.append(
                ModuleDescriptor(
                    name=m.name,
                    perceptor=m.perceptor,
                    analyzer=m.analyzer,
                    orchestrator=m.orchestrator,
                    responder=m.responder,
                    enabled=True,
                    priority=priority,
                )
            )
        return sorted(active, key=lambda x: (x.priority, x.name))
