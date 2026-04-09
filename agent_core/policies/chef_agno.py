from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class ChefAgnoPolicy:
    """
    Persona / política de alto nível — não contém o algoritmo PAOR.

    Define limites, prioridades e critérios consumidos pelo Planner e Reflector.
    Troca de persona = nova instância desta configuração, sem alterar o mecanismo.
    """

    name: str = "chef_agno"
    priorities: tuple[str, ...] = ()
    max_iterations: int = 10
    decision_style: str = "balanced"  # ex.: conservative | balanced | aggressive
    success_criteria: dict[str, Any] = field(default_factory=dict)
    limits: dict[str, Any] = field(
        default_factory=lambda: {
            "max_actions_per_iteration": 3,
            "timeout_seconds": 300,
        }
    )
    require_human_before_act: bool = False
    metadata: dict[str, Any] = field(default_factory=dict)

    def validate(self) -> None:
        if self.max_iterations < 1:
            raise ValueError("max_iterations deve ser >= 1")
