from __future__ import annotations

from typing import Any

from agent_core.policies.chef_agno import ChefAgnoPolicy


class Reflector:
    """
    REFLECT: compara observações com objetivo e critérios da política.

    Critérios de sucesso vêm de `policy.success_criteria` e `semantic_context` (Core).
    """

    def reflect(
        self,
        *,
        objective: str,
        policy: ChefAgnoPolicy,
        semantic_context: dict[str, Any],
        observations: list[dict[str, Any]],
        iteration: int,
    ) -> dict[str, Any]:
        criteria = policy.success_criteria
        external_match = semantic_context.get("completion_signals", [])

        all_ok = all(o.get("success", False) for o in observations) if observations else False
        goal_reached = all_ok and self._matches_criteria(observations, criteria, external_match)

        suggested_adjustments: list[dict[str, Any]] = []
        if not goal_reached and iteration < policy.max_iterations:
            suggested_adjustments = [
                {
                    "operation": semantic_context.get("fallback_operation", "noop"),
                    "target": "retry",
                    "params": {"reason": "criteria_not_met"},
                }
            ]

        gov = semantic_context.get("governanca") or {}
        return {
            "iteration": iteration,
            "goal_reached": goal_reached,
            "summary": {
                "objective": objective,
                "observation_count": len(observations),
                "criteria_keys": list(criteria.keys()),
                "architecture_score_at_plan_time": gov.get("score_arquitetural"),
            },
            "suggested_adjustments": suggested_adjustments,
        }

    def _matches_criteria(
        self,
        observations: list[dict[str, Any]],
        criteria: dict[str, Any],
        signals: list[Any],
    ) -> bool:
        if criteria.get("require_all_steps_ok") is True:
            return all(o.get("success") for o in observations)
        if signals:
            return any(s in str(observations) for s in signals)
        return len(observations) > 0
