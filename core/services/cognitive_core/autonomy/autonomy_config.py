"""
Níveis de autonomia (Fase 3) — controlável por ambiente.
0=off, 1=insights, 2=sugestões de ação, 3=execução automática (com safety + DecisionEngine).
"""
from __future__ import annotations

import os


def get_autonomy_level() -> int:
    raw = (os.getenv("COGNITIVE_AUTONOMY_LEVEL") or "0").strip()
    try:
        v = int(raw)
    except ValueError:
        v = 0
    return max(0, min(3, v))


def get_min_confidence_for_auto() -> float:
    try:
        return float(os.getenv("COGNITIVE_AUTONOMY_MIN_CONFIDENCE", "0.72"))
    except ValueError:
        return 0.72


def get_max_risk_for_auto() -> str:
    """risk_level permitido para execução no nível 3 (low|medium|high)."""
    return (os.getenv("COGNITIVE_AUTONOMY_MAX_RISK_AUTO") or "medium").strip().lower()


def get_execute_tool_name() -> str:
    """Tool MCP usada na execução automática (default seguro: noop)."""
    return (os.getenv("COGNITIVE_AUTONOMY_EXECUTE_TOOL") or "noop").strip()


def is_autonomy_enabled() -> bool:
    return get_autonomy_level() >= 1


def get_max_proposals_per_cycle() -> int:
    try:
        return max(1, min(10, int(os.getenv("COGNITIVE_AUTONOMY_MAX_PROPOSALS", "3"))))
    except ValueError:
        return 3


def get_max_insights_for_actions() -> int:
    """Quantos insights ranqueados geram candidatos (evita explosão combinatória)."""
    try:
        return max(1, min(15, int(os.getenv("COGNITIVE_AUTONOMY_MAX_INSIGHTS", "5"))))
    except ValueError:
        return 5
