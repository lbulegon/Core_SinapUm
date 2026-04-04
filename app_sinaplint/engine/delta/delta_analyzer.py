"""
Núcleo de comparação baseline vs HEAD (relatórios completos do orquestrador).
"""

from __future__ import annotations

from typing import Any

from app_sinaplint.engine.delta.delta_formatter import format_delta_summary


def _arch(r: dict[str, Any]) -> dict[str, Any]:
    return dict(r.get("architecture") or {})


def _cycles_set(arch: dict[str, Any]) -> set[frozenset[str]]:
    out: set[frozenset[str]] = set()
    for cyc in arch.get("cycles") or []:
        if isinstance(cyc, list) and cyc:
            out.add(frozenset(cyc))
    return out


def _total_edge_weight(arch: dict[str, Any]) -> int:
    edges = arch.get("edges_weighted") or []
    if edges:
        return sum(int(e.get("weight", 0)) for e in edges)
    ctx = arch.get("_context") if isinstance(arch.get("_context"), dict) else {}
    m = (ctx.get("metrics") or {}) if isinstance(ctx, dict) else {}
    return int(m.get("total_dependency_weight") or 0)


def _coupling_score_sum(arch: dict[str, Any]) -> int:
    coup = arch.get("coupling") or {}
    scores = coup.get("coupling_score") or {}
    if isinstance(scores, dict):
        return sum(int(v) for v in scores.values())
    return 0


def compute_delta(current: dict[str, Any], base: dict[str, Any]) -> dict[str, Any]:
    """
    Evolução entre duas análises (HEAD = ``current``, baseline = ``base``).

    Inclui:
    - ``new_cycles_count`` / ``removed_cycles_count``: diferença de **conjuntos** SCC (preciso).
    - ``new_cycles`` / ``resolved_cycles``: diferença de **contagens** de grupos (heurística simples).
    - Acoplamento por peso de arestas e por soma de ``coupling_score`` por app.
    """
    ac = _arch(current)
    ab = _arch(base)

    cs = int(current.get("score") or 0)
    bs = int(base.get("score") or 0)
    score_change = cs - bs

    sc = current.get("scores") or {}
    sb = base.get("scores") or {}
    arch_sc = int(sc.get("architecture") or 0)
    arch_sb = int(sb.get("architecture") or 0)
    architecture_score_change = arch_sc - arch_sb

    cyc_c = ac.get("cycles") or []
    cyc_b = ab.get("cycles") or []
    cycles_count_change = len(cyc_c) - len(cyc_b)

    new_cycles = max(len(cyc_c) - len(cyc_b), 0)
    resolved_cycles = max(len(cyc_b) - len(cyc_c), 0)

    set_c = _cycles_set(ac)
    set_b = _cycles_set(ab)
    new_cycle_groups = len(set_c - set_b)
    removed_cycle_groups = len(set_b - set_c)

    tw_c = _total_edge_weight(ac)
    tw_b = _total_edge_weight(ab)
    if not tw_c and not tw_b:
        m_c = (current.get("_context") or {}).get("metrics") or {}
        m_b = (base.get("_context") or {}).get("metrics") or {}
        tw_c = int(m_c.get("total_dependency_weight") or 0)
        tw_b = int(m_b.get("total_dependency_weight") or 0)

    coupling_increased = tw_c > tw_b
    coupling_decreased = tw_c < tw_b
    coupling_delta = tw_c - tw_b

    csum_c = _coupling_score_sum(ac)
    csum_b = _coupling_score_sum(ab)
    coupling_score_sum_delta = csum_c - csum_b
    coupling_score_increased = csum_c > csum_b
    coupling_score_decreased = csum_c < csum_b

    rk_c = (ac.get("insights") or {}).get("risk") or {}
    rk_b = (ab.get("insights") or {}).get("risk") or {}
    risk_change = int(rk_c.get("risk_score") or 0) - int(rk_b.get("risk_score") or 0)

    if score_change < 0 or new_cycle_groups > 0 or (coupling_increased and coupling_delta > 2):
        trend = "worsened"
    elif score_change > 0 and new_cycle_groups == 0 and not coupling_increased:
        trend = "improved"
    else:
        trend = "mixed"

    return {
        "base_available": True,
        "score_change": score_change,
        "score_before": bs,
        "score_after": cs,
        "architecture_score_change": architecture_score_change,
        "cycles_count_change": cycles_count_change,
        "new_cycles": new_cycles,
        "resolved_cycles": resolved_cycles,
        "new_cycles_count": new_cycle_groups,
        "removed_cycles_count": removed_cycle_groups,
        "coupling_increased": coupling_increased,
        "coupling_decreased": coupling_decreased,
        "total_dependency_weight_delta": coupling_delta,
        "coupling_score_sum_base": csum_b,
        "coupling_score_sum_head": csum_c,
        "coupling_score_sum_delta": coupling_score_sum_delta,
        "coupling_score_increased": coupling_score_increased,
        "coupling_score_decreased": coupling_score_decreased,
        "risk_score_change": risk_change,
        "trend": trend,
    }


class DeltaAnalyzer:
    """Fachada explícita para comparar dois relatórios completos."""

    def compare(self, base_result: dict[str, Any], head_result: dict[str, Any]) -> dict[str, Any]:
        """``head_result`` = estado atual; ``base_result`` = baseline."""
        return compute_delta(head_result, base_result)


def enrich_head_with_delta(
    head_result: dict[str, Any],
    base_result: dict[str, Any],
    *,
    base_ref: str = "",
    resolved_ref: str = "",
) -> dict[str, Any]:
    """Copia ``head_result``, acrescenta ``delta`` e ``delta_summary``."""
    out = dict(head_result)
    delta = compute_delta(head_result, base_result)
    if base_ref:
        delta["base_ref"] = base_ref
    if resolved_ref:
        delta["resolved_ref"] = resolved_ref
    out["delta"] = delta
    out["delta_summary"] = format_delta_summary(delta)
    return out
