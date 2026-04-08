"""
Fachada do processamento da fila de comandos.

A persistência e o ORM ficam em `services.command_execution_runtime`; aqui só se expõe a API.
"""

from __future__ import annotations

from typing import Any


def execute_pending(context: dict[str, Any] | None = None) -> int:
    from services.command_execution_runtime import CommandExecutionRuntime

    return CommandExecutionRuntime.execute_pending(context)
