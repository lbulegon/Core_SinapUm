"""Registo de módulos built-in (`AgentCoreConfig.ready`)."""

from __future__ import annotations

from agent_core.modules.environmental.module import EnvironmentalModule
from agent_core.registry.module_registry import ModuleRegistry


def register_builtin_modules() -> None:
    ModuleRegistry.register(EnvironmentalModule.descriptor())
