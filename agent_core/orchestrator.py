from __future__ import annotations

import logging
from typing import Any, Callable

from agent_core.adapters.orbital_adapter import OrbitalExecutionError
from agent_core.environmental_pipeline import enrich_semantic_context
from agent_core.executor import Executor
from agent_core.models.agent_run import AgentRun
from agent_core.observer import Observer
from agent_core.planner import Planner
from agent_core.policies.chef_agno import ChefAgnoPolicy
from agent_core.reflector import Reflector
from agent_core.state_manager import StateManager

logger = logging.getLogger(__name__)

# Hook opcional: (run, phase, context) -> True continua, False pausa para humano
HumanInterventionHook = Callable[[AgentRun, str, dict[str, Any]], bool]


class CognitiveOrchestrator:
    """
    Mecanismo PAOR: não contém regras semânticas — apenas orquestra portas e persistência.

    `semantic_context` é sempre injetado pelo chamador (Core_SinapUm) e tratado como opaco.
    """

    def __init__(
        self,
        state_manager: StateManager,
        planner: Planner,
        executor: Executor,
        observer: Observer,
        reflector: Reflector,
        *,
        human_hook: HumanInterventionHook | None = None,
    ) -> None:
        self._state = state_manager
        self._planner = planner
        self._executor = executor
        self._observer = observer
        self._reflector = reflector
        self._human_hook = human_hook

    def run_cycle(
        self,
        *,
        objective: str,
        policy: ChefAgnoPolicy,
        semantic_context: dict[str, Any],
        initial_state: dict[str, Any] | None = None,
    ) -> AgentRun:
        policy.validate()
        run = self._state.create_run(objective, initial_state)
        semantic_context = enrich_semantic_context(dict(semantic_context), initial_state)

        try:
            prior_reflection: dict[str, Any] | None = None
            iteration = 1

            while iteration <= policy.max_iterations:
                self._state.update_iteration(run, iteration, {"phase": "plan", "iteration": iteration})

                # —— PLAN ——
                plan_input = {
                    "objective": objective,
                    "iteration": iteration,
                    "prior_reflection": prior_reflection,
                }
                plan = self._planner.plan(
                    objective=objective,
                    policy=policy,
                    semantic_context=semantic_context,
                    iteration=iteration,
                    prior_reflection=prior_reflection,
                )
                self._state.set_plan(run, plan)
                self._state.append_audit(
                    run,
                    phase="plan",
                    input_data=plan_input,
                    output_data=plan,
                    decision="plan_accepted",
                )

                if self._human_hook and not self._human_hook(run, "plan", {"plan": plan}):
                    self._state.set_status(run, AgentRun.Status.AWAITING_HUMAN)
                    return self._state.refresh(run)

                observations: list[dict[str, Any]] = []

                for step in plan.get("steps", []):
                    if policy.require_human_before_act and self._human_hook:
                        if not self._human_hook(run, "before_act", {"step": step}):
                            self._state.set_status(run, AgentRun.Status.AWAITING_HUMAN)
                            return self._state.refresh(run)

                    # —— ACT ——
                    act_input = {"step": step}
                    try:
                        raw = self._executor.execute_step(step)
                    except OrbitalExecutionError as exc:
                        logger.warning("Falha orbital controlada: %s", exc)
                        self._state.append_audit(
                            run,
                            phase="act",
                            input_data=act_input,
                            output_data={"error": str(exc)},
                            decision="act_failed",
                        )
                        self._validate_action_output({}, semantic_context, failed=True)
                        self._state.set_status(run, AgentRun.Status.FAILED, error_message=str(exc))
                        return self._state.refresh(run)

                    self._validate_action_output(raw, semantic_context, failed=False)
                    self._state.append_audit(
                        run,
                        phase="act",
                        input_data=act_input,
                        output_data=raw,
                        decision="act_ok",
                    )

                    # —— OBSERVE ——
                    obs = self._observer.observe(step=step, raw_result=raw)
                    observations.append(obs)
                    self._state.append_audit(
                        run,
                        phase="observe",
                        input_data={"step": step, "raw": raw},
                        output_data=obs,
                        decision="observed",
                    )

                # —— REFLECT ——
                reflection = self._reflector.reflect(
                    objective=objective,
                    policy=policy,
                    semantic_context=semantic_context,
                    observations=observations,
                    iteration=iteration,
                )
                self._state.append_audit(
                    run,
                    phase="reflect",
                    input_data={"observations": observations},
                    output_data=reflection,
                    decision="goal_reached" if reflection.get("goal_reached") else "continue",
                )

                prior_reflection = reflection
                estado = {
                    "last_reflection": reflection,
                    "iteration": iteration,
                    "phase": "post_reflect",
                    "governanca": semantic_context.get("governanca"),
                    "environmental_mode": semantic_context.get("environmental_mode"),
                }
                self._state.update_iteration(run, iteration, estado)

                if reflection.get("goal_reached"):
                    self._state.set_status(run, AgentRun.Status.COMPLETED)
                    return self._state.refresh(run)

                iteration += 1

            self._state.set_status(
                run,
                AgentRun.Status.FAILED,
                error_message="Limite de iterações atingido (fail-safe)",
            )
            return self._state.refresh(run)

        except Exception as exc:  # noqa: BLE001 — último recurso; estado gravado
            logger.exception("Falha inesperada no orquestrador")
            self._state.set_status(run, AgentRun.Status.FAILED, error_message=str(exc))
            return self._state.refresh(run)

    def _validate_action_output(
        self,
        raw: dict[str, Any],
        semantic_context: dict[str, Any],
        *,
        failed: bool,
    ) -> None:
        """Validação estrutural pós-ação — chaves exigidas vêm do Core via semantic_context."""
        if failed:
            return
        required = semantic_context.get("required_result_keys", [])
        for key in required:
            if key not in raw:
                raise ValueError(f"Resultado orbital sem chave obrigatória: {key}")
