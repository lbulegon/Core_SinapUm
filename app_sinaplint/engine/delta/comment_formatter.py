"""
Markdown “premium” para comentário único no PR (CI).
"""

from __future__ import annotations

from typing import Any

from app_sinaplint.engine.delta.delta_formatter import summarize_delta


def generate_pr_comment(
    result: dict[str, Any],
    *,
    short_sha: str = "",
    base_label: str = "",
) -> str:
    """
    Gera corpo Markdown completo (inclui marcador HTML para atualização idempotente).

    ``result`` deve ser o dict completo do orquestrador (com ``delta`` opcional).
    """
    lines: list[str] = [
        "<!-- sinaplint-ci -->",
        "",
        "## 🧠 SinapLint Analysis",
        "",
    ]

    if short_sha:
        lines.append(f"_Commit `{short_sha}`_")
        lines.append("")

    score = result.get("score")
    scores = result.get("scores") or {}
    arch_score = scores.get("architecture")

    emoji = "🟢" if (score is not None and score >= 80) else "🟡" if (score is not None and score >= 60) else "🔴"
    lines.append(
        f"**Score:** {emoji} `{score}/100` — **{result.get('quality', '—')}**"
    )
    if arch_score is not None:
        lines.append("")
        lines.append(f"**Arquitetura (subscore):** `{arch_score}`")
    lines.append("")

    blocking = result.get("blocking") or {}
    if blocking.get("blocked"):
        lines.append("### 🚫 Política de bloqueio")
        lines.append("")
        for r in blocking.get("reasons") or []:
            lines.append(f"- {r}")
        if blocking.get("delta_policy_note"):
            lines.append("")
            lines.append(f"_{blocking['delta_policy_note']}_")
        lines.append("")

    arch = result.get("architecture") or {}
    ins = arch.get("insights") or {}
    risk = ins.get("risk") or {}
    if risk.get("risk_score") is not None:
        lines.append(
            f"**Risco:** `{risk.get('risk_score')}` ({risk.get('risk_level', '—')})"
        )
        crit = risk.get("critical_apps") or []
        if crit:
            lines.append("**Apps críticos:** " + ", ".join(crit[:8]))
        lines.append("")

    delta = result.get("delta") or {}
    lines.append("### 📊 Alterações vs base")
    lines.append("")
    if delta.get("base_available"):
        bl = base_label or delta.get("base_ref") or delta.get("resolved_ref") or "baseline"
        lines.append(f"_Comparado com `{bl}`._")
        lines.append("")
        ch = delta.get("score_change")
        if ch is not None and ch != 0:
            sign = "+" if ch > 0 else ""
            lines.append(f"- **Score:** {sign}{ch} (de `{delta.get('score_before')}` para `{delta.get('score_after')}`)")
        lines.append(f"- **Tendência:** `{delta.get('trend', '—')}`")
        lines.append(f"- **Arquitetura (Δ):** `{delta.get('architecture_score_change', '—')}`")
        if delta.get("new_cycles_count"):
            lines.append(f"- ⚠️ **Novos grupos SCC:** `{delta['new_cycles_count']}`")
        if delta.get("coupling_increased"):
            lines.append("- ⚠️ **Acoplamento (peso de arestas):** aumentou vs base")
        if delta.get("coupling_decreased"):
            lines.append("- ✅ **Acoplamento (peso de arestas):** diminuiu vs base")
        ds = result.get("delta_summary") or ""
        if ds:
            lines.append("")
            lines.append(f"> {ds}")
        lines.append("")
        lines.append("**Resumo:**")
        for s in summarize_delta(delta):
            lines.append(f"- {s}")
    else:
        reason = delta.get("reason", "unknown")
        lines.append(f"_Delta não disponível (`{reason}`)._")
    lines.append("")

    plan = (ins.get("refactor_plan") or result.get("refactor_plan") or [])[:5]
    lines.append("### 🔥 Prioridade de refactor")
    lines.append("")
    if plan:
        for item in plan[:3]:
            app = item.get("app", "—")
            prio = item.get("priority", "—")
            lines.append(f"- **{app}** (`{prio}`) — impacto `{item.get('impact_score', '—')}`")
            for action in (item.get("actions") or [])[:4]:
                lines.append(f"  - {action}")
        if len(plan) > 3:
            lines.append("")
            lines.append(f"_… e mais {len(plan) - 3} entrada(s) no plano completo (JSON)._")
    else:
        lines.append("_Nenhuma ação crítica listada — ótimo._ 🎉")
    lines.append("")

    lines.append("---")
    lines.append("_Gerado por SinapLint · artefacto `sinaplint-report`_")
    return "\n".join(lines)
