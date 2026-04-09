from __future__ import annotations

from typing import Any

from agent_core.adapters.orbital_adapter import OrbitalExecutionError
from agent_core.ports.orbital_port import OrbitalPort


class Executor:
    """
    Camada ACT: traduz passos do plano em chamadas à porta orbital.

    Validação estrutural mínima pós-construção da ação — regras de domínio ficam no Core.
    """

    def __init__(self, port: OrbitalPort) -> None:
        self._port = port

    def execute_step(self, step: dict[str, Any]) -> dict[str, Any]:
        self._validate_step(step)
        action = {
            "operation": step.get("operation"),
            "target": step.get("target"),
            "params": step.get("params", {}),
        }
        try:
            return self._port.execute(action)
        except OrbitalExecutionError:
            raise
        except Exception as exc:  # noqa: BLE001
            raise OrbitalExecutionError(str(exc)) from exc

    def _validate_step(self, step: dict[str, Any]) -> None:
        if not step.get("operation"):
            raise ValueError("Passo do plano sem 'operation'")
