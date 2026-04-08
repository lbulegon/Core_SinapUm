from __future__ import annotations

from typing import Any


class BaseCommandHandler:
    """Contrato para um comando operacional (extensível por domínio)."""

    command_name: str | None = None

    def can_execute(self, command: Any) -> bool:
        return True

    def execute(self, command: Any, context: dict[str, Any] | None) -> Any:
        raise NotImplementedError

    def on_success(self, command: Any, result: Any) -> None:
        pass

    def on_failure(self, command: Any, error: str) -> None:
        pass
