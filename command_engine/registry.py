from __future__ import annotations

from typing import Type

from command_engine.base import BaseCommandHandler


class CommandRegistry:
    """Registo global de handlers por `command_name` (instâncias)."""

    _handlers: dict[str, BaseCommandHandler] = {}

    @classmethod
    def register(cls, handler_class: Type[BaseCommandHandler]) -> None:
        name = handler_class.command_name
        if not name:
            raise ValueError(f"Handler sem command_name: {handler_class}")
        cls._handlers[name] = handler_class()

    @classmethod
    def get(cls, command_name: str) -> BaseCommandHandler | None:
        return cls._handlers.get(command_name)

    @classmethod
    def all(cls) -> dict[str, BaseCommandHandler]:
        return dict(cls._handlers)

    @classmethod
    def clear(cls) -> None:
        cls._handlers = {}
