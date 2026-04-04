"""
Interpretação do grafo: anti-padrões (god app), prioridade de refactor, risco global e heatmap.

Usa apenas dados já produzidos por ``build_architecture_report`` (sem novo scan em disco).
"""

from __future__ import annotations

from typing import Any

from app_sinaplint.engine.graph.refactor_plan import RefactorPlanGenerator
from app_sinaplint.engine.graph.refactor_priority import RefactorImpactAnalyzer

# Ajustáveis (MVP; podem vir de settings no futuro)
GOD_APP_FAN_IN_MIN = 8
GOD_APP_OUT_DEGREE_MIN = 5
CYCLE_WEIGHT_PER_PARTICIPATION = 15


def _cycle_participation(cycles: list[list[str]]) -> dict[str, int]:
    """Quantas SCCs (ciclos) cada app participa."""
    count: dict[str, int] = {}
    for scc in cycles:
        for app in scc:
            count[app] = count.get(app, 0) + 1
    return count


def detect_god_apps(
    fan_in: dict[str, int],
    coupling_score: dict[str, int],
    *,
    fan_in_min: int = GOD_APP_FAN_IN_MIN,
    out_degree_min: int = GOD_APP_OUT_DEGREE_MIN,
) -> list[dict[str, Any]]:
    """Apps com fan-in e grau de saída elevados (hub + muitas dependências)."""
    out: list[dict[str, Any]] = []
    for app in sorted(set(fan_in.keys()) | set(coupling_score.keys())):
        fi = int(fan_in.get(app, 0))
        od = int(coupling_score.get(app, 0))
        if fi >= fan_in_min and od >= out_degree_min:
            out.append(
                {
                    "type": "god_app",
                    "app": app,
                    "reason": "alto fan-in + alto acoplamento de saída",
                    "fan_in": fi,
                    "out_degree": od,
                }
            )
    return out


def compute_refactor_priority(
    fan_in: dict[str, int],
    coupling_score: dict[str, int],
    cycle_part: dict[str, int],
) -> list[dict[str, Any]]:
    """
    ``priority = fan_in * 2 + out_degree + cycle_weight``,
    onde ``cycle_weight = participações_em_SCC * CYCLE_WEIGHT_PER_PARTICIPATION``.
    """
    apps = set(fan_in.keys()) | set(coupling_score.keys()) | set(cycle_part.keys())
    rows: list[tuple[int, str, str]] = []
    for app in apps:
        fi = int(fan_in.get(app, 0))
        od = int(coupling_score.get(app, 0))
        cw = int(cycle_part.get(app, 0)) * CYCLE_WEIGHT_PER_PARTICIPATION
        priority = fi * 2 + od + cw
        reason_parts: list[str] = []
        if fi:
            reason_parts.append(f"fan-in {fi}")
        if od:
            reason_parts.append(f"saídas {od}")
        if cycle_part.get(app, 0):
            reason_parts.append(f"em {cycle_part[app]} ciclo(s)")
        reason = " + ".join(reason_parts) if reason_parts else "baixo impacto estrutural"
        rows.append((priority, app, reason))

    rows.sort(key=lambda x: (-x[0], x[1]))
    return [
        {
            "app": app,
            "priority": int(pri),
            "reason": reason,
        }
        for pri, app, reason in rows
    ]


def compute_architectural_risk(
    cycles: list[list[str]],
    fan_in: dict[str, int],
    coupling_score: dict[str, int],
    cycle_part: dict[str, int],
    *,
    critical_apps_override: list[str] | None = None,
) -> dict[str, Any]:
    """Score 0–100, nível e apps mais críticos (prioridade de refactor)."""
    n_cycles = len(cycles)
    max_fan = max(fan_in.values()) if fan_in else 0
    max_out = max(coupling_score.values()) if coupling_score else 0
    nodes_in_cycles = sum(len(s) for s in cycles)

    risk = 0
    risk += min(35, n_cycles * 12)
    risk += min(25, max_fan * 2)
    risk += min(25, max_out * 3)
    risk += min(15, nodes_in_cycles * 2)
    risk = int(min(100, risk))

    if risk >= 70:
        level = "high"
    elif risk >= 40:
        level = "medium"
    else:
        level = "low"

    if critical_apps_override is not None:
        critical = [a for a in critical_apps_override if a][:5]
    else:
        prio = compute_refactor_priority(fan_in, coupling_score, cycle_part)
        critical = [p["app"] for p in prio[:5] if p["priority"] > 0][:5]
        if not critical and prio:
            critical = [prio[0]["app"]]

    return {
        "risk_score": risk,
        "risk_level": level,
        "critical_apps": critical,
    }


def enrich_visual_heatmap(
    visual: dict[str, list[dict[str, Any]]],
    fan_in: dict[str, int],
    coupling_score: dict[str, int],
    cycle_part: dict[str, int],
    impact_by_app: dict[str, dict[str, Any]] | None = None,
) -> dict[str, list[dict[str, Any]]]:
    """Acrescenta ``size``, ``color``, ``risk_tier``, ``risk_index`` (0–100) por nó; opcionalmente métricas de impacto."""
    nodes = list(visual.get("nodes") or [])
    raw: dict[str, float] = {}
    for n in nodes:
        aid = n.get("id") or ""
        if not aid:
            continue
        fi = int(fan_in.get(aid, 0))
        od = int(coupling_score.get(aid, 0))
        cp = int(cycle_part.get(aid, 0))
        raw[aid] = float(fi * 2 + od + cp * CYCLE_WEIGHT_PER_PARTICIPATION)

    max_r = max(raw.values()) if raw else 1.0
    if max_r < 1e-6:
        max_r = 1.0

    out_nodes: list[dict[str, Any]] = []
    for n in nodes:
        aid = n.get("id") or ""
        idx = int(round(100 * (raw.get(aid, 0.0) / max_r)))
        if idx >= 67:
            tier = "high"
            color = "#dc2626"
        elif idx >= 34:
            tier = "medium"
            color = "#f59e0b"
        else:
            tier = "low"
            color = "#22c55e"
        size = 12 + int(28 * (idx / 100.0))
        enriched = dict(n)
        enriched["risk_index"] = idx
        enriched["risk"] = idx  # alias para frontends (ex.: react-force-graph)
        enriched["risk_tier"] = tier
        enriched["color"] = color
        enriched["size"] = size
        if impact_by_app and aid in impact_by_app:
            im = impact_by_app[aid]
            enriched["impact_score"] = im.get("impact_score")
            enriched["dependencies"] = im.get("dependencies")
            enriched["in_cycles"] = im.get("in_cycles")
            enriched["fan_in"] = im.get("fan_in")
            enriched["high_coupling"] = im.get("high_coupling")
        out_nodes.append(enriched)

    return {"nodes": out_nodes, "edges": list(visual.get("edges") or [])}


def build_insights_payload(arch: dict[str, Any]) -> dict[str, Any]:
    """Agrega anti-padrões, prioridade, impacto, plano executivo, risco e visual com heatmap."""
    graph = arch.get("graph") or {}
    coupling = arch.get("coupling") or {}
    coupling_score = dict(coupling.get("coupling_score") or {})
    fan_in = dict(arch.get("fan_in") or {})
    cycles = list(arch.get("cycles") or [])
    visual = dict(arch.get("visual") or {"nodes": [], "edges": []})

    cycle_part = _cycle_participation(cycles)

    anti_patterns: list[dict[str, Any]] = []
    for g in detect_god_apps(fan_in, coupling_score):
        anti_patterns.append(g)

    refactor_priority = compute_refactor_priority(fan_in, coupling_score, cycle_part)

    impact_analysis = RefactorImpactAnalyzer().compute(arch)
    refactor_plan = RefactorPlanGenerator().generate(impact_analysis)
    critical_from_impact = [row["app"] for row in impact_analysis[:5]]
    risk = compute_architectural_risk(
        cycles,
        fan_in,
        coupling_score,
        cycle_part,
        critical_apps_override=critical_from_impact,
    )
    impact_by_app = {row["app"]: row for row in impact_analysis}
    visual_heat = enrich_visual_heatmap(
        visual, fan_in, coupling_score, cycle_part, impact_by_app
    )

    return {
        "anti_patterns": anti_patterns,
        "refactor_priority": refactor_priority,
        "impact_analysis": impact_analysis,
        "refactor_plan": refactor_plan,
        "risk": risk,
        "visual": visual_heat,
    }
