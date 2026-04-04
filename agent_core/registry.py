"""Vista declarativa do registro (documentação); runtime: `agent_core.registry.module_registry`."""

from __future__ import annotations

from agent_core.modules.environmental.module import EnvironmentalModule
from agent_core.registry.module_registry import ModuleDescriptor, ModuleRegistry

_env = EnvironmentalModule.descriptor()

MODULES: list[dict[str, object]] = [
    {
        "name": _env.name,
        "perceptor": _env.perceptor,
        "analyzer": _env.analyzer,
        "orchestrator": _env.orchestrator,
        "responder": _env.responder,
        "enabled": True,
    }
]

__all__ = ["MODULES", "ModuleRegistry", "ModuleDescriptor"]
