from __future__ import annotations

import importlib
from typing import Any

from agent_core.core.interfaces import Analyzer, Orchestrator, Perceptor, Responder

# Não importar agent/engine aqui: `module_registry` importa `interfaces` e um import
# ansioso de `engine` cria ciclo (engine → registry → interfaces → core.__init__ → engine).

__all__ = [
    "AgentCore",
    "SinapEngine",
    "Perceptor",
    "Analyzer",
    "Orchestrator",
    "Responder",
]


def __getattr__(name: str) -> Any:
    if name == "AgentCore":
        return importlib.import_module("agent_core.core.agent").AgentCore
    if name == "SinapEngine":
        return importlib.import_module("agent_core.core.engine").SinapEngine
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
