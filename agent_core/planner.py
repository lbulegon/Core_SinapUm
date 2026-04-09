from __future__ import annotations

import uuid
from typing import Any

from agent_core.policies.chef_agno import ChefAgnoPolicy


class Planner:
    """
    Gera planos estruturados a partir do objetivo, política e contexto semântico externo.

    Não define regras de domínio: `semantic_context` vem do Core_SinapUm (fonte de verdade).
    Aqui só há heurística de orquestração — em produção pode delegar a LLM com saída validada.
    """

    def plan(
        self,
        *,
        objective: str,
        policy: ChefAgnoPolicy,
        semantic_context: dict[str, Any],
        iteration: int,
        prior_reflection: dict[str, Any] | None,
    ) -> dict[str, Any]:
        plan_id = str(uuid.uuid4())
        steps: list[dict[str, Any]] = []

        # Heurística mínima: incorporar prioridades da política e restrições do Core (opacas).
        constraints = semantic_context.get("constraints", [])
        allowed_ops = semantic_context.get("allowed_operations", ["noop", "dispatch"])

        gov = semantic_context.get("governanca") or {}
        score = gov.get("score_arquitetural")
        governance_adjustment = self._governance_tier(score)

        max_actions = int(policy.limits.get("max_actions_per_iteration", 3))
        if governance_adjustment == "conservative":
            max_actions = max(1, min(max_actions, 1))
        elif governance_adjustment == "cautious":
            max_actions = max(1, min(max_actions, 2))

        env_mode = semantic_context.get("environmental_mode", "NORMAL")
        environmental_adjustment = self._environmental_tier(env_mode)
        if environmental_adjustment == "emergency":
            max_actions = max(1, min(max_actions, 1))
        elif environmental_adjustment == "pressure":
            max_actions = max(1, min(max_actions, 2))

        sys_mode_raw = semantic_context.get("system_mode", "NORMAL")
        sys_mode = sys_mode_raw if isinstance(sys_mode_raw, str) else "NORMAL"
        sm = sys_mode.strip().upper()
        if sm == "CRITICAL":
            max_actions = max(1, min(max_actions, 1))
        elif sm == "PRESSURE":
            max_actions = max(1, min(max_actions, 2))

        prios = policy.priorities[:max_actions]

        def _step_params(extra: dict[str, Any] | None = None) -> dict[str, Any]:
            base: dict[str, Any] = {
                "environmental_mode": env_mode,
                "environmental_analysis": semantic_context.get("environmental_analysis"),
                "system_mode": sys_mode_raw if isinstance(sys_mode_raw, str) else "NORMAL",
            }
            if extra:
                base.update(extra)
            return base

        for prio in prios:
            steps.append(
                {
                    "id": str(uuid.uuid4()),
                    "operation": allowed_ops[0] if allowed_ops else "noop",
                    "target": prio,
                    "params": _step_params({"semantic_hints": constraints}),
                }
            )

        if not steps:
            steps = [
                {
                    "id": str(uuid.uuid4()),
                    "operation": allowed_ops[0] if allowed_ops else "noop",
                    "target": "default",
                    "params": _step_params({"objective": objective}),
                }
            ]

        if prior_reflection and prior_reflection.get("suggested_adjustments"):
            steps.extend(
                self._adjustments_as_steps(
                    prior_reflection["suggested_adjustments"],
                    allowed_ops,
                    base_params=_step_params(),
                )
            )

        return {
            "plan_id": plan_id,
            "iteration": iteration,
            "steps": steps,
            "policy_name": policy.name,
            "style": policy.decision_style,
            "governance_adjustment": governance_adjustment,
            "governance_score_observed": score,
            "institutional_recommendations_preview": (gov.get("recomendacoes") or [])[:5],
            "environmental_mode": env_mode,
            "environmental_adjustment": environmental_adjustment,
            "system_mode": sys_mode_raw if isinstance(sys_mode_raw, str) else "NORMAL",
        }

    @staticmethod
    def _governance_tier(score: Any) -> str:
        """
        Metadado de planejamento derivado do parecer institucional (não é regra de domínio).
        """
        if score is None:
            return "unknown"
        try:
            s = float(score)
        except (TypeError, ValueError):
            return "unknown"
        if s < 6.0:
            return "conservative"
        if s < 8.0:
            return "cautious"
        return "normal"

    @staticmethod
    def _environmental_tier(mode: Any) -> str:
        """Heurística de planejamento a partir do modo ambiental (PAOR — Orchestrate)."""
        m = (mode or "NORMAL") if isinstance(mode, str) else "NORMAL"
        m = m.strip().upper()
        if m == "EMERGENCY_MODE":
            return "emergency"
        if m == "PRESSURE_CONTROL":
            return "pressure"
        return "normal"

    def _adjustments_as_steps(
        self,
        adjustments: list[dict[str, Any]],
        allowed_ops: list[str],
        *,
        base_params: dict[str, Any] | None = None,
    ) -> list[dict[str, Any]]:
        out: list[dict[str, Any]] = []
        base = dict(base_params or {})
        for adj in adjustments:
            merged = dict(base)
            merged.update(adj.get("params") or {})
            out.append(
                {
                    "id": str(uuid.uuid4()),
                    "operation": adj.get("operation", allowed_ops[0] if allowed_ops else "noop"),
                    "target": adj.get("target", "adjustment"),
                    "params": merged,
                }
            )
        return out
