"""
Loop: pattern → insight → action → DecisionEngine → (opcional) ACP.
"""
from __future__ import annotations

import uuid
from typing import Any, Dict, List, Optional, Tuple

from app_acp.task_manager import TaskManager

from core.services.cognitive_core.actions.action_generator import ActionGenerator, ActionProposal
from core.services.cognitive_core.autonomy import autonomy_config
from core.services.cognitive_core.autonomy.autonomy_logging import log_autonomy
from core.services.cognitive_core.autonomy.autonomy_simulation import simulate_autonomy_proposal
from core.services.cognitive_core.autonomy.safety_validator import validate_auto_execution, validate_context_minimum
from core.services.cognitive_core.context.cognitive_context import CognitiveContext
from core.services.cognitive_core.insights.insight_engine import InsightEngine
from core.services.cognitive_core.mediation.decision_engine import DecisionEngine
from core.services.cognitive_core.patterns.pattern_engine import PatternEngine
from core.services.cognitive_core.perception.adapters import perception_from_mcp_dict
from core.services.cognitive_core.reality.builder import RealityStateBuilder
from core.services.cognitive_core.strategic.insight_ranker import RankedInsight, StrategyEvaluator
from core.services.cognitive_core.strategic.strategic_context import (
    OBJECTIVE_INCREASE_MARGIN,
    StrategicContext,
)


def _default_namespaces() -> List[str]:
    return ["mrfoo", "global"]


def _select_proposals_with_simulation(
    *,
    ranked: List[RankedInsight],
    action_generator: ActionGenerator,
    dynamic_metrics: Dict[str, Any],
    operational_live: Dict[str, Any],
    strategic_context: StrategicContext,
) -> Tuple[List[ActionProposal], List[Dict[str, Any]]]:
    """
    Por insight ranqueado: gera candidatos, simula, escolhe o melhor; depois ordena globalmente e corta ao máximo configurado.
    """
    max_ins = autonomy_config.get_max_insights_for_actions()
    max_prop = autonomy_config.get_max_proposals_per_cycle()
    picks: List[Tuple[ActionProposal, float, Dict[str, Any], str]] = []

    for ri in ranked[:max_ins]:
        cands = action_generator.candidates_for_insight(ri.insight)
        best: Optional[ActionProposal] = None
        best_combined = -1.0
        best_sim: Dict[str, Any] = {}
        for c in cands:
            sim = simulate_autonomy_proposal(
                c,
                dynamic_metrics=dynamic_metrics,
                operational_live=operational_live,
            )
            margin_bonus = 0.0
            if OBJECTIVE_INCREASE_MARGIN in strategic_context.objetivos and sim.get("margin_pressure", 0) > 0:
                margin_bonus = 0.1 * strategic_context.weight_for(OBJECTIVE_INCREASE_MARGIN)
            combined = 0.52 * ri.strategic_score + 0.43 * float(sim.get("composite") or 0) + margin_bonus
            if combined > best_combined:
                best_combined = combined
                best = c
                best_sim = {**sim, "combined_score": round(combined, 4)}
        if best:
            picks.append((best, best_combined, best_sim, ri.insight.insight_id))
            log_autonomy(
                "action_chosen",
                payload={
                    "insight_id": ri.insight.insight_id,
                    "action_key": best.action_key,
                    "combined_score": round(best_combined, 4),
                    "simulation": best_sim,
                },
            )

    picks.sort(key=lambda x: x[1], reverse=True)
    trace = [
        {
            "insight_id": iid,
            "action_key": p.action_key,
            "combined_score": round(sc, 4),
            "simulation": sim,
        }
        for p, sc, sim, iid in picks[:max_prop]
    ]
    return [p[0] for p in picks[:max_prop]], trace


def run_autonomous_cycle(
    *,
    tenant_id: str,
    operational_live: Optional[Dict[str, Any]] = None,
    dynamic_metrics: Optional[Dict[str, Any]] = None,
    trace_id: Optional[str] = None,
    strategic_context: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """
    Executa um ciclo completo. Respeita COGNITIVE_AUTONOMY_LEVEL.
    Pipeline: pattern → insight → ranking estratégico → candidatos → simulação → escolha → DecisionEngine → safety → execução.
    """
    level = autonomy_config.get_autonomy_level()
    tid = str(tenant_id).strip()
    trace_id = trace_id or f"autonomy-{uuid.uuid4().hex[:16]}"
    operational_live = operational_live or {}
    dynamic_metrics = dynamic_metrics or {}

    result: Dict[str, Any] = {
        "ok": True,
        "autonomy_level": level,
        "trace_id": trace_id,
        "patterns": [],
        "insights": [],
        "proposals": [],
        "ranked_insights": [],
        "chosen_plan": [],
        "decisions": [],
        "executed_tasks": [],
        "skipped_reason": None,
    }
    plan_trace: List[Dict[str, Any]] = []

    if level < 1:
        result["skipped_reason"] = "autonomy_disabled"
        log_autonomy("cycle_skipped", trace_id=trace_id, tenant_id=tid, payload={"reason": "level_0"})
        return result

    ok_ctx, ctx_reasons = validate_context_minimum(tenant_id=tid, operational_live=operational_live)
    if not ok_ctx:
        result["ok"] = False
        result["skipped_reason"] = ctx_reasons
        return result

    pe = PatternEngine()
    matches = pe.run(
        tenant_id=tid,
        operational_live=operational_live,
        dynamic_metrics=dynamic_metrics,
    )
    result["patterns"] = [m.pattern_key for m in matches]

    ie = InsightEngine()
    insights = ie.from_patterns(matches)
    result["insights"] = [{"id": i.insight_id, "kind": i.kind, "pattern": i.pattern_key} for i in insights]

    sctx = StrategicContext.from_payload(strategic_context)
    sctx.tenant_id = tid
    ranked = StrategyEvaluator.rank_insights(
        insights, sctx, dynamic_metrics=dynamic_metrics
    )
    result["ranked_insights"] = [
        {
            "insight_id": r.insight.insight_id,
            "pattern": r.insight.pattern_key,
            "strategic_score": r.strategic_score,
            "alignment": r.alignment,
        }
        for r in ranked
    ]

    try:
        from app_inbound_events.models import AutonomyActionLog, CognitivePatternMemory

        for m in matches:
            CognitivePatternMemory.objects.create(
                tenant_id=tid,
                pattern_key=m.pattern_key,
                confidence=m.confidence,
                signals_json=m.signals,
                trace_id=trace_id,
            )
    except Exception:
        pass

    if level < 2:
        result["skipped_reason"] = "insights_only"
        log_autonomy("cycle_insights_only", trace_id=trace_id, tenant_id=tid, payload=result)
        return result

    ag = ActionGenerator()
    proposals, plan_trace = _select_proposals_with_simulation(
        ranked=ranked,
        action_generator=ag,
        dynamic_metrics=dynamic_metrics,
        operational_live=operational_live,
        strategic_context=sctx,
    )
    result["proposals"] = [p.action_key for p in proposals]
    result["chosen_plan"] = plan_trace

    sim_by_action = {row["action_key"]: row.get("simulation") for row in plan_trace}

    engine = DecisionEngine()
    builder = RealityStateBuilder(default_namespaces=_default_namespaces())

    for prop in proposals:
        raw = {
            **prop.mcp_input,
            "text": prop.mcp_input.get("text") or f"autonomy:{prop.action_key}",
            "trace_id": trace_id,
            "context_hint": {
                **(prop.mcp_input.get("context_hint") or {}),
                "tenant_id": tid,
                "autonomy_action": prop.action_key,
            },
        }
        perception = perception_from_mcp_dict(raw, source="autonomy", trace_id=trace_id)
        ctx = CognitiveContext.from_perception(
            perception,
            extra={"rag_namespaces": _default_namespaces()},
        )
        reality = builder.build(perception, ctx)
        decision = engine.decide_orbital_support(perception=perception, reality=reality, ctx=ctx)
        decision.metadata = {
            **(decision.metadata or {}),
            "autonomy": True,
            "proposal": prop.action_key,
            "trace_id": trace_id,
            "strategic_objectives": sctx.objetivos,
            "autonomy_simulation": sim_by_action.get(prop.action_key) or {},
        }
        result["decisions"].append(
            {
                "action_key": prop.action_key,
                "decision": decision.to_dict(),
            }
        )

        log_autonomy(
            "decision_for_autonomy",
            trace_id=trace_id,
            tenant_id=tid,
            payload={"proposal": prop.action_key, "engine_action": decision.action},
        )

        final_status = "proposed"
        task_id: Optional[str] = None
        extra: Dict[str, Any] = {}

        if level < 3:
            _persist_action_log(
                tenant_id=tid,
                trace_id=trace_id,
                proposal=prop,
                decision_dict=decision.to_dict(),
                level=level,
                status=final_status,
            )
            continue

        safe, reasons = validate_auto_execution(decision, prop)
        if not safe:
            final_status = "blocked"
            extra = {"reasons": reasons}
            log_autonomy(
                "action_blocked",
                trace_id=trace_id,
                tenant_id=tid,
                payload={"reasons": reasons, "proposal": prop.action_key},
            )
            _persist_action_log(
                tenant_id=tid,
                trace_id=trace_id,
                proposal=prop,
                decision_dict=decision.to_dict(),
                level=level,
                status=final_status,
                extra_outcome=extra,
            )
            continue

        exec_tool = autonomy_config.get_execute_tool_name()
        payload = {
            "tool": prop.mcp_tool if prop.mcp_tool != "noop" else exec_tool,
            "input": prop.mcp_input,
            "decision_output": decision.to_dict(),
        }
        if payload["tool"] == "noop":
            payload["input"] = {
                **prop.mcp_input,
                "autonomy_trace": trace_id,
                "decision_snapshot": decision.to_dict(),
            }

        tm = TaskManager()
        task = tm.create_task(
            agent_name="cognitive_autonomy",
            payload=payload,
            trace_id=trace_id,
            idempotency_key=f"autonomy:{trace_id}:{prop.action_key}",
        )
        result["executed_tasks"].append(task)
        task_id = str(task.get("task_id") or "")
        log_autonomy(
            "action_executed",
            trace_id=trace_id,
            tenant_id=tid,
            payload={"task": task, "proposal": prop.action_key},
        )
        _persist_action_log(
            tenant_id=tid,
            trace_id=trace_id,
            proposal=prop,
            decision_dict=decision.to_dict(),
            level=level,
            status="executed",
            task_id=task_id,
        )

    log_autonomy(
        "outcome",
        trace_id=trace_id,
        tenant_id=tid,
        payload={
            "patterns": len(result["patterns"]),
            "insights": len(result["insights"]),
            "tasks": len(result["executed_tasks"]),
            "proposals_executed_plan": len(plan_trace),
        },
    )

    if level >= 2 and plan_trace:
        _record_autonomy_strategic_feedback(
            tenant_id=tid,
            trace_id=trace_id,
            plan_trace=plan_trace,
            ranked_summary=result.get("ranked_insights") or [],
        )

    return result


def _record_autonomy_strategic_feedback(
    *,
    tenant_id: str,
    trace_id: str,
    plan_trace: List[Dict[str, Any]],
    ranked_summary: List[Dict[str, Any]],
) -> None:
    try:
        from core.services.cognitive_core.strategic.strategy_feedback_store import record_strategy_feedback

        scores = [float(x.get("simulation", {}).get("combined_score") or 0) for x in plan_trace]
        pred = sum(scores) / len(scores) if scores else 0.0
        record_strategy_feedback(
            tenant_id=tenant_id,
            strategy_key="autonomy_prioritized_cycle",
            proposal_id=trace_id[:128],
            predicted_impact=pred,
            payload={"plan_trace": plan_trace, "ranked_insights": ranked_summary},
        )
    except Exception:
        pass


def _persist_action_log(
    *,
    tenant_id: str,
    trace_id: str,
    proposal: ActionProposal,
    decision_dict: Dict[str, Any],
    level: int,
    status: str,
    task_id: Optional[str] = None,
    extra_outcome: Optional[Dict[str, Any]] = None,
) -> None:
    try:
        from app_inbound_events.models import AutonomyActionLog

        AutonomyActionLog.objects.create(
            tenant_id=tenant_id[:64],
            trace_id=trace_id[:128],
            proposal_key=proposal.action_key[:128],
            mcp_tool=proposal.mcp_tool[:128],
            decision_json=decision_dict,
            autonomy_level=level,
            status=status[:32],
            acp_task_id=(task_id or "")[:64],
            outcome_json=extra_outcome or {},
        )
    except Exception:
        pass
