from __future__ import annotations

from typing import Any

from agent_core.adapters.architecture_intelligence_adapter import ArchitectureIntelligenceAdapter
from agent_core.adapters.orbital_adapter import OrbitalAdapter
from agent_core.executor import Executor
from agent_core.orchestrator import CognitiveOrchestrator, HumanInterventionHook
from agent_core.observer import Observer
from agent_core.planner import Planner
from agent_core.policies.chef_agno import ChefAgnoPolicy
from agent_core.ports.orbital_port import OrbitalPort
from agent_core.reflector import Reflector
from agent_core.state_manager import StateManager


class CognitiveCycleService:
    """
    Fachada de aplicação: monta o grafo de dependências sem acoplar orbitais concretos.

    Quem chama (ex.: views do Core_SinapUm) injeta `semantic_context` produzido pela ontologia.
    """

    def __init__(
        self,
        *,
        orbital_port: OrbitalPort,
        state_manager: StateManager | None = None,
        human_hook: HumanInterventionHook | None = None,
    ) -> None:
        self._state = state_manager or StateManager()
        self._orchestrator = CognitiveOrchestrator(
            state_manager=self._state,
            planner=Planner(),
            executor=Executor(orbital_port),
            observer=Observer(),
            reflector=Reflector(),
            human_hook=human_hook,
        )

    @classmethod
    def with_simulated_orbital(
        cls,
        *,
        human_hook: HumanInterventionHook | None = None,
        orbital_backend: Any = None,
    ) -> CognitiveCycleService:
        """Conveniência para testes: adaptador simulado, sem rede."""
        adapter = OrbitalAdapter(backend=orbital_backend, simulate=orbital_backend is None)
        return cls(orbital_port=adapter, human_hook=human_hook)

    def run(
        self,
        *,
        objective: str,
        policy: ChefAgnoPolicy,
        semantic_context: dict[str, Any],
        initial_state: dict[str, Any] | None = None,
    ):
        """
        Executa um ciclo cognitivo completo até sucesso, falha ou intervenção humana.

        `semantic_context` deve ser montado pelo Core (restrições, operações permitidas, chaves esperadas).
        """
        return self._orchestrator.run_cycle(
            objective=objective,
            policy=policy,
            semantic_context=semantic_context,
            initial_state=initial_state,
        )

    def run_with_architecture_governance(
        self,
        *,
        objective: str,
        policy: ChefAgnoPolicy,
        semantic_context: dict[str, Any],
        bundle_path: str,
        evaluation_mode: str = "full_cycle",
        system_name: str = "MrFoo",
        system_type: str = "Orbital",
        architecture_adapter: ArchitectureIntelligenceAdapter | None = None,
        initial_state: dict[str, Any] | None = None,
        trace_id: str | None = None,
    ):
        """
        Loop PAOR com parecer institucional injetado antes do PLAN.

        A avaliação vem de Architecture Intelligence (interno ou HTTP); o Agent Core apenas consome
        o resultado como `semantic_context["governanca"]` — não redefine critérios arquiteturais.
        """
        adapter = architecture_adapter or ArchitectureIntelligenceAdapter()
        evaluation = adapter.fetch_evaluation(
            bundle_path=bundle_path,
            evaluation_mode=evaluation_mode,
            system_name=system_name,
            system_type=system_type,
            trace_id=trace_id,
        )
        merged = adapter.merge_into_semantic_context(semantic_context, evaluation)
        base_state = dict(initial_state or {})
        base_state.setdefault("architecture_evaluation", evaluation)
        return self.run(
            objective=objective,
            policy=policy,
            semantic_context=merged,
            initial_state=base_state,
        )
