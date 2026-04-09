"""Fachada Django para o motor cognitivo."""

from __future__ import annotations

from typing import Any

from agent_core.core.engine import SinapEngine


class SinapEngineService:
    def __init__(self) -> None:
        self._engine = SinapEngine()

    def execute(self, context: dict[str, Any]) -> dict[str, Any]:
        return self._engine.run(context)
