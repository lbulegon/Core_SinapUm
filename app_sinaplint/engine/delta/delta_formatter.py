"""
Texto legível para logs, sumários e PR (delta).
"""

from __future__ import annotations

from typing import Any


def format_delta_summary(delta: dict[str, Any]) -> str:
    """Uma linha curta (Markdown leve) para Summary / rodapé."""
    if not delta.get("base_available"):
        return ""
    parts: list[str] = []
    sc = int(delta.get("score_change") or 0)
    parts.append(f"Score {delta.get('score_before')} → {delta.get('score_after')} ({sc:+d})")
    if delta.get("new_cycles_count"):
        parts.append(f"+{delta['new_cycles_count']} grupo(s) SCC novo(s)")
    if delta.get("new_cycles") and not delta.get("new_cycles_count"):
        parts.append(f"+{delta['new_cycles']} grupo(s) de ciclo (contagem)")
    if delta.get("coupling_increased"):
        parts.append("peso de dependências aumentou")
    if delta.get("coupling_score_increased"):
        parts.append("soma coupling_score aumentou")
    parts.append(f"tendência: **{delta.get('trend')}**")
    return " · ".join(parts)


def summarize_delta(delta: dict[str, Any]) -> list[str]:
    """
    Lista de frases com emoji (para comentários ou secções rich).

    Compatível com o contrato ``delta`` de :func:`compute_delta`.
    """
    if not delta.get("base_available"):
        return ["_Delta indisponível (baseline não analisada)._"]

    summary: list[str] = []
    sc = int(delta.get("score_change") or 0)
    if sc < 0:
        summary.append(f"📉 Score caiu ({sc:+d})")
    elif sc > 0:
        summary.append(f"📈 Score subiu (+{sc})")

    ncc = int(delta.get("new_cycles_count") or 0)
    if ncc > 0:
        summary.append(f"⚠️ {ncc} novo(s) grupo(s) SCC (ciclos) em relação à base")

    nc = int(delta.get("new_cycles") or 0)
    if nc > 0 and not ncc:
        summary.append(f"⚠️ {nc} novo(s) grupo(s) de ciclo (contagem simples)")

    rc = int(delta.get("resolved_cycles") or 0)
    if rc > 0:
        summary.append(f"✅ {rc} grupo(s) de ciclo a menos (contagem)")

    rem = int(delta.get("removed_cycles_count") or 0)
    if rem > 0:
        summary.append(f"✅ {rem} grupo(s) SCC removido(s) (conjunto)")

    if delta.get("coupling_increased"):
        summary.append("⚠️ Peso de dependências entre apps aumentou")
    elif delta.get("coupling_decreased"):
        summary.append("✅ Peso de dependências entre apps diminuiu")

    if delta.get("coupling_score_increased"):
        summary.append("⚠️ Soma de coupling por app aumentou")
    elif delta.get("coupling_score_decreased"):
        summary.append("✅ Soma de coupling por app diminuiu")

    if not summary:
        summary.append(f"➡️ Tendência: **{delta.get('trend', 'mixed')}**")

    return summary
