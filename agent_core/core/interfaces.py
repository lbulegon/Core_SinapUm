from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any


class Perceptor(ABC):
    @abstractmethod
    def perceive(self, context: dict[str, Any]) -> dict[str, Any] | None:
        pass


class Analyzer(ABC):
    @abstractmethod
    def analyze(self, perception: dict[str, Any]) -> dict[str, Any]:
        pass


class Orchestrator(ABC):
    @abstractmethod
    def decide(self, analyses: list[dict[str, Any]]) -> str | None:
        pass


class Responder(ABC):
    @abstractmethod
    def handle(self, decision: str, context: dict[str, Any]) -> dict[str, Any] | None:
        pass
