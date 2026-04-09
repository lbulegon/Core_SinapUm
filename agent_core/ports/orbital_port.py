from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any


class OrbitalPort(ABC):
    """
    Porta hexagonal para execução em orbitais.

    O Agent Core nunca importa implementações concretas de orbitais;
    apenas esta interface. Contrato estável: dict in / dict out (versionável via schema).
    """

    @abstractmethod
    def execute(self, action: dict[str, Any]) -> dict[str, Any]:
        """
        Executa uma ação operacional descrita de forma estruturada.

        Raises:
            OrbitalExecutionError: falha controlada do adaptador (fail-safe no orquestrador).
        """
        raise NotImplementedError
