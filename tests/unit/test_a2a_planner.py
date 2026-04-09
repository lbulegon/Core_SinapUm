"""
Testes unitários do PlannerAgent (fallback rule-based, step noop).
PR5 — Hardening + testes.
"""
import sys
from pathlib import Path

_root = Path(__file__).resolve().parents[2]
if str(_root) not in sys.path:
    sys.path.insert(0, str(_root))

from a2a.planner_agent import PlannerAgent
from a2a.schemas import A2APlan


class TestPlannerAgent:
    """PlannerAgent: plano com steps; fallback para noop quando sem match."""

    def test_plan_returns_a2a_plan(self):
        planner = PlannerAgent()
        plan = planner.plan(user_input="qualquer coisa")
        assert isinstance(plan, A2APlan)
        assert plan.intent
        assert isinstance(plan.steps, list)
        assert len(plan.steps) >= 1

    def test_plan_fallback_noop_when_no_pattern(self):
        planner = PlannerAgent()
        plan = planner.plan(user_input="xyz sem padrão conhecido 123")
        assert plan.intent == "fallback_safe"
        assert len(plan.steps) == 1
        assert plan.steps[0].tool_name == "noop"
        assert "no_matching_pattern" in (plan.steps[0].args or {}).get("reason", "")

    def test_plan_matches_analise_produto(self):
        planner = PlannerAgent()
        plan = planner.plan(user_input="analisar produto da imagem")
        assert len(plan.steps) == 1
        assert plan.steps[0].tool_name == "vitrinezap.analisar_produto"
        assert plan.steps[0].timeout_seconds == 60

    def test_plan_matches_catalogo(self):
        planner = PlannerAgent()
        plan = planner.plan(user_input="listar produtos do catálogo")
        assert len(plan.steps) == 1
        assert plan.steps[0].tool_name == "vitrinezap.catalog.compose"

    def test_plan_step_has_required_fields(self):
        planner = PlannerAgent()
        plan = planner.plan(user_input="analisar imagem")
        step = plan.steps[0]
        assert step.id
        assert step.tool_name
        assert isinstance(step.args, dict)
