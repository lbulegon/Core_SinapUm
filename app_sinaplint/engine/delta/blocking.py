"""
Políticas de bloqueio de merge/CI com base no relatório e no ``delta`` (vs baseline).
"""

from __future__ import annotations

import json
import os
from copy import deepcopy
from pathlib import Path
from typing import Any

DEFAULT_RULES: dict[str, Any] = {
    "fail_under_score": 80,
    "block_on_new_cycles": True,
    # Novos grupos SCC (conjunto) — mais fiável que a contagem simples de listas.
    "use_scc_new_groups": True,
    "block_on_coupling_increase": True,
    # Ignorar ruído: só bloqueia se o peso subir mais que N unidades (0 = qualquer aumento).
    "min_coupling_weight_delta": 0,
    "block_on_coupling_score_increase": False,
    # score_change < max_score_drop bloqueia (ex.: -5 → bloqueia -6 ou pior).
    "max_score_drop": -5,
}

_POLICY_KEYS = set(DEFAULT_RULES.keys())


def load_blocking_rules(policy_path: Path | str | None = None) -> dict[str, Any]:
    """
    Mescla ``DEFAULT_RULES`` com JSON de ficheiro ou ``SINAPLINT_POLICY_JSON``.
    """
    rules = deepcopy(DEFAULT_RULES)
    path = policy_path
    if path is None:
        env = (os.environ.get("SINAPLINT_POLICY_JSON") or "").strip()
        if env:
            path = Path(env)
    if path:
        p = Path(path)
        if p.is_file():
            extra = json.loads(p.read_text(encoding="utf-8"))
            if isinstance(extra, dict):
                for k, v in extra.items():
                    if k in _POLICY_KEYS:
                        rules[k] = v
    return rules


class DeltaBlocker:
    """Avalia se o resultado viola políticas (score, delta arquitetural)."""

    def __init__(self, rules: dict[str, Any] | None = None) -> None:
        self.rules = deepcopy(DEFAULT_RULES)
        if rules:
            self.rules.update(rules)

    def evaluate(self, result: dict[str, Any]) -> dict[str, Any]:
        score = int(result.get("score") or 0)
        delta = result.get("delta") or {}
        base_ok = bool(delta.get("base_available"))
        policy_note = ""

        reasons: list[str] = []
        blocked = False

        min_score = int(self.rules["fail_under_score"])
        if score < min_score:
            blocked = True
            reasons.append(f"Score abaixo do mínimo ({score} < {min_score})")

        if base_ok:
            use_scc = bool(self.rules.get("use_scc_new_groups", True))
            new_c = (
                int(delta.get("new_cycles_count") or 0)
                if use_scc
                else int(delta.get("new_cycles") or 0)
            )
            if self.rules.get("block_on_new_cycles") and new_c > 0:
                blocked = True
                reasons.append(
                    f"{new_c} novo(s) grupo(s) de ciclo arquitetural (SCC) vs baseline"
                )

            min_w = int(self.rules.get("min_coupling_weight_delta") or 0)
            twd = int(delta.get("total_dependency_weight_delta") or 0)
            if self.rules.get("block_on_coupling_increase") and delta.get("coupling_increased"):
                if twd >= min_w:
                    blocked = True
                    reasons.append(
                        f"Aumento de acoplamento (peso de dependências +{twd} vs baseline)"
                    )

            if self.rules.get("block_on_coupling_score_increase") and delta.get(
                "coupling_score_increased"
            ):
                blocked = True
                reasons.append("Aumento da soma coupling_score por app vs baseline")

            max_drop = int(self.rules["max_score_drop"])
            sc = int(delta.get("score_change") or 0)
            if sc < max_drop:
                blocked = True
                reasons.append(
                    f"Queda de score acima do limite ({sc} < {max_drop})"
                )
        else:
            dr = delta.get("reason", "sem_delta")
            policy_note = (
                "Regras de delta (ciclos, acoplamento, queda de score) ignoradas: "
                f"baseline indisponível ({dr})."
            )

        out: dict[str, Any] = {
            "blocked": blocked,
            "reasons": reasons,
            "rules": {k: self.rules[k] for k in DEFAULT_RULES.keys() if k in self.rules},
        }
        out["delta_policy_skipped"] = not base_ok
        if policy_note:
            out["delta_policy_note"] = policy_note
        return out


def format_blocking_message(blocking: dict[str, Any], *, locale: str = "pt") -> str:
    """Texto Markdown curto para PR ou log."""
    if not blocking.get("blocked"):
        if locale == "pt":
            return "✅ Nenhum bloqueio ativo pelas regras configuradas."
        return "✅ No blocking issues detected."

    lines = ["## 🚫 Merge bloqueado pelo SinapLint", ""]
    for r in blocking.get("reasons") or []:
        lines.append(f"- {r}")
    lines.append("")
    if locale == "pt":
        lines.append("Resolve ou ajusta a política antes de fazer merge.")
    else:
        lines.append("Resolve these issues before merging.")
    return "\n".join(lines)
