"""
Comparação "antes" do relatório SinapLint — útil para dry-run de impacto (sem reescrever arquivos).
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from sinaplint.engine import SinapLint
from sinaplint.scorers.module_score import total_module_penalty


class SimulationService:
    """Simula ganho hipotético de score (placeholder até métricas por arquivo)."""

    @staticmethod
    def estimate_score_after_cleanup(
        base_path: Path | None = None,
        *,
        assumed_issue_reduction: int = 1,
    ) -> dict[str, Any]:
        """
        `assumed_issue_reduction`: número de issues que desapareceriam após refactor (heurística).

        Distribui a redução: estrutura → padrão → AST (igual à prioridade de correção típica).
        """
        root = base_path or Path(__file__).resolve().parent.parent
        lint = SinapLint(root).run()
        before = int(lint["score"])

        st_err = len(lint["structure"]["errors"])
        pat = len(lint["pattern_issues"])
        ast_n = len(lint["ast_issues"])
        modules = lint.get("modules") or []
        mod_pen = total_module_penalty(modules)

        st2 = max(0, st_err - min(assumed_issue_reduction, st_err))
        rem = assumed_issue_reduction - (st_err - st2)
        pat2 = max(0, pat - min(rem, pat))
        rem -= pat - pat2
        ast2 = max(0, ast_n - min(rem, ast_n))

        engine = SinapLint(root)
        after = engine.calculate_score(
            ["s"] * st2,
            pat2,
            ast2,
            mod_pen,
        )

        return {
            "before": before,
            "after": after,
            "assumed_issue_reduction": assumed_issue_reduction,
            "note": "Estimativa; use reduções reais por tipo de issue para precisão.",
        }
