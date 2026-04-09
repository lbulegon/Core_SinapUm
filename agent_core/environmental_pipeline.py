"""
Ponte Agent Core ↔ motor cognitivo: enriquece `semantic_context`.
"""

from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


def _ensure_sinapcore_bootstrap() -> None:
    from agent_core.registry.bootstrap import register_builtin_modules
    from agent_core.registry.module_registry import ModuleRegistry

    if not ModuleRegistry.all_modules():
        register_builtin_modules()


def orchestrate_environmental(analyses: List[Dict[str, Any]]) -> str:
    for a in analyses:
        if a.get("severity") == "critical":
            return "EMERGENCY_MODE"
        if a.get("severity") == "high":
            return "PRESSURE_CONTROL"
    return "NORMAL"


def _mode_from_sinapcore_decisions(decisions: List[str]) -> str:
    if "ENV_CRITICAL" in decisions:
        return "EMERGENCY_MODE"
    if "ENV_PRESSURE" in decisions:
        return "PRESSURE_CONTROL"
    return "NORMAL"


def _legacy_perception(perceptions: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
    for p in perceptions:
        if p.get("module") != "environmental":
            continue
        data = p.get("data") or {}
        return {
            "type": "environmental",
            "state": data.get("state"),
            "score": data.get("score"),
            "confidence": data.get("confidence", 0.0),
            "timestamp": data.get("timestamp"),
        }
    return None


def _legacy_analysis(analyses: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
    for a in analyses:
        if a.get("module") == "environmental":
            return {
                "severity": a.get("severity"),
                "action": a.get("action"),
                "state": a.get("state"),
                "score": a.get("score"),
            }
    return None


def enrich_semantic_context(
    semantic_context: Dict[str, Any],
    initial_state: Optional[Dict[str, Any]],
) -> Dict[str, Any]:
    ctx = dict(semantic_context)
    eid = ctx.get("estabelecimento_id")
    if eid is None and initial_state:
        eid = initial_state.get("estabelecimento_id")

    if eid is None:
        ctx.setdefault("environmental_mode", "NORMAL")
        ctx.setdefault("environmental_perception", None)
        ctx.setdefault("environmental_analysis", None)
        ctx.setdefault("system_mode", "NORMAL")
        return ctx

    try:
        from services.environmental_state_service import EnvironmentalStateService
        from services.system_mode_service import compute_mode_from_env_dict

        raw_env = EnvironmentalStateService.get_state(eid)
        ctx["system_mode"] = compute_mode_from_env_dict(raw_env)
    except Exception:
        ctx.setdefault("system_mode", "NORMAL")

    _ensure_sinapcore_bootstrap()

    try:
        from agent_core.core.engine import SinapEngine

        full_ctx: Dict[str, Any] = {**ctx}
        if initial_state:
            full_ctx.update(initial_state)
        full_ctx.setdefault("estabelecimento_id", eid)

        result = SinapEngine().run(full_ctx)
        perceptions = result.get("perceptions") or []
        analyses = result.get("analyses") or []
        decisions = result.get("decisions") or []

        ctx["sinapcore"] = result
        ctx["environmental_perception"] = _legacy_perception(perceptions)
        ctx["environmental_analysis"] = _legacy_analysis(analyses)
        ctx["environmental_mode"] = _mode_from_sinapcore_decisions(decisions)

        if not ctx["environmental_perception"]:
            ctx["environmental_analysis"] = None
            ctx["environmental_mode"] = "NORMAL"

    except Exception:
        logger.exception("Falha ao enriquecer contexto cognitivo")
        ctx.setdefault("environmental_mode", "NORMAL")
        ctx.setdefault("environmental_perception", None)
        ctx.setdefault("environmental_analysis", None)
        ctx.setdefault("system_mode", "NORMAL")

    return ctx
