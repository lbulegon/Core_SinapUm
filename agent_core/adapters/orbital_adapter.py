from __future__ import annotations

import logging
from typing import Any, Callable

from agent_core.ports.orbital_port import OrbitalPort

logger = logging.getLogger(__name__)


class OrbitalExecutionError(Exception):
    """Erro encapsulado da camada orbital — permite fail-safe no orquestrador."""


class OrbitalAdapter(OrbitalPort):
    """
    Adaptador concreto: simula orbitais ou delega a cliente HTTP/gRPC/etc.

    Injeção de `backend` permite testes e troca de transporte sem alterar o Core cognitivo.
    """

    def __init__(
        self,
        backend: Callable[[dict[str, Any]], dict[str, Any]] | None = None,
        *,
        simulate: bool = True,
    ) -> None:
        self._simulate = simulate
        self._backend = backend

    def execute(self, action: dict[str, Any]) -> dict[str, Any]:
        if self._backend is not None:
            try:
                return self._backend(action)
            except Exception as exc:  # noqa: BLE001 — fronteira de adaptador
                logger.exception("Falha no backend orbital")
                raise OrbitalExecutionError(str(exc)) from exc

        if self._simulate:
            return self._simulate_execution(action)

        raise OrbitalExecutionError("Adaptador sem backend e simulate=False")

    def _simulate_execution(self, action: dict[str, Any]) -> dict[str, Any]:
        """Resposta determinística para testes — não é regra de negócio, só eco estruturado."""
        op = action.get("operation", "noop")
        return {
            "ok": True,
            "simulated": True,
            "echo_operation": op,
            "payload_summary": {k: action.get(k) for k in ("target", "params") if k in action},
        }
