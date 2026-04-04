"""
Motor SinapLint: orquestra regras, scoring e resultado agregado.

Camada de domínio (regras + score + IA heurística). O orquestrador de alto nível
está em ``orchestrator.py``.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from app_sinaplint.ai_refactor import SinapAIRefactor
from app_sinaplint.rules.ast_rules import check_ast
from app_sinaplint.rules.module_rules import check_modules
from app_sinaplint.rules.pattern_rules import check_patterns
from app_sinaplint.rules.structure_rules import check_structure
from app_sinaplint.scorers.module_score import total_module_penalty

MIN_PASS_SCORE = 80

PENALTIES = {
    "structure": 10,
    "pattern": 15,
    "ast": 12,
}


def _dedupe_issues(issues: list[dict[str, str]]) -> list[dict[str, str]]:
    seen: set[tuple[str, str]] = set()
    out: list[dict[str, str]] = []
    for i in issues:
        k = (i.get("path", ""), i.get("message", ""))
        if k in seen:
            continue
        seen.add(k)
        out.append(i)
    return out


def quality_label(score: int) -> str:
    if score >= 90:
        return "EXCELENTE"
    if score >= MIN_PASS_SCORE:
        return "ACEITÁVEL"
    return "BLOQUEADO"


class SinapLint:
    """
    Linter cognitivo + arquitetural: estrutura, regex, módulos PAOR, AST.
    """

    def __init__(self, base_path: Path | None = None) -> None:
        # engine/sinap_lint.py → …/app_sinaplint/engine/ → …/app_sinaplint/ → raiz Core_SinapUm
        _default_root = Path(__file__).resolve().parent.parent.parent
        self.base_path = Path(base_path) if base_path is not None else _default_root

    def run(self) -> dict[str, Any]:
        structure = check_structure(self.base_path)
        pattern_data = check_patterns(self.base_path)
        modules = check_modules(self.base_path)
        ast_raw = _dedupe_issues(check_ast(self.base_path))

        structure_errors = structure["errors"]
        pattern_issues = _dedupe_issues(pattern_data["issues"])
        suggestions = pattern_data.get("suggestions", [])

        score = 100
        score -= len(structure_errors) * PENALTIES["structure"]
        score -= len(pattern_issues) * PENALTIES["pattern"]
        score -= len(ast_raw) * PENALTIES["ast"]
        score -= total_module_penalty(modules)
        score = max(0, score)

        q = quality_label(score)
        ok = score >= MIN_PASS_SCORE

        ai = SinapAIRefactor()
        ai_refactor: list[dict[str, Any]] = []
        for e in structure_errors:
            issue = {"path": "", "message": e}
            s = ai.suggest(issue)
            ai_refactor.append({"kind": "structure", "issue": issue, "ai": s})
        for p in pattern_issues:
            ai_refactor.append({"kind": "pattern", "issue": p, "ai": ai.suggest(p)})
        for a in ast_raw:
            ai_refactor.append({"kind": "ast", "issue": a, "ai": ai.suggest(a)})

        return {
            "score": score,
            "quality": q,
            "ok": ok,
            "min_pass_score": MIN_PASS_SCORE,
            "structure": {
                "dirs_ok": structure["dirs_ok"],
                "files_ok": structure["files_ok"],
                "errors": structure_errors,
            },
            "pattern_issues": pattern_issues,
            "suggestions": suggestions,
            "modules": modules,
            "ast_issues": ast_raw,
            "penalties": PENALTIES,
            "ai_refactor": ai_refactor,
        }

    def calculate_score(
        self,
        structure_errors: list[str],
        pattern_count: int,
        ast_count: int,
        module_penalty: int,
    ) -> int:
        """Útil para testes ou recomputação manual."""
        score = 100
        score -= len(structure_errors) * PENALTIES["structure"]
        score -= pattern_count * PENALTIES["pattern"]
        score -= ast_count * PENALTIES["ast"]
        score -= module_penalty
        return max(0, score)
