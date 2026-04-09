"""
Agent Core (DeepAgents) — mecanismo de loop cognitivo PAOR.

Não importe este pacote no topo antes de django.setup(); use submódulos explícitos,
ex.: `from agent_core.services.cognitive_cycle_service import CognitiveCycleService`.

INSTALLED_APPS: `agent_core.apps.AgentCoreConfig`
"""

from __future__ import annotations

import importlib
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from agent_core.apps import AgentCoreConfig as AgentCoreConfigType
    from agent_core.services.cognitive_cycle_service import CognitiveCycleService as CognitiveCycleServiceType

__all__ = ["CognitiveCycleService", "AgentCoreConfig"]


def __getattr__(name: str) -> Any:
    if name == "CognitiveCycleService":
        return importlib.import_module(
            "agent_core.services.cognitive_cycle_service"
        ).CognitiveCycleService
    if name == "AgentCoreConfig":
        return importlib.import_module("agent_core.apps").AgentCoreConfig
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
