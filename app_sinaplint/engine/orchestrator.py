"""
Orquestrador do motor SinapLint — ponto único entre pipeline e ``SinapLint``.

Não duplica regras: delega para :class:`app_sinaplint.engine.sinap_lint.SinapLint`,
onde já estão structure / pattern / modules / AST e ``ai_refactor``.

Enriquece o resultado com ``_context`` (apps Django, grafo de dependências),
``scores`` por camada, ``architecture`` (grafo + SCC) e ``clean_architecture``
(camadas + plano de refactor), sem alterar ``score`` / ``quality`` / ``ok``.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from app_sinaplint.engine.architecture import build_clean_architecture_report
from app_sinaplint.engine.context_builder import AnalysisContextBuilder
from app_sinaplint.engine.graph import build_architecture_report, compute_architecture_score
from app_sinaplint.engine.sinap_lint import MIN_PASS_SCORE, SinapLint


class SinapLintOrchestrator:
    """Cérebro fino: escolhe raiz do projeto e executa o motor existente."""

    def run(self, project_path: Path | str | None = None) -> dict[str, Any]:
        """
        Executa análise completa sobre ``project_path``.

        Se ``project_path`` for None, usa a raiz do monólito Core_SinapUm
        (pai do pacote ``app_sinaplint``).
        """
        if project_path is None:
            base: Path | None = None
        else:
            base = Path(project_path).resolve()
        lint = SinapLint(base_path=base)
        result = lint.run()

        root = lint.base_path
        builder = AnalysisContextBuilder()
        arch = build_architecture_report(root)
        result["_context"] = builder.build_from_arch(root, arch)
        result["architecture"] = {
            "graph": arch["graph"],
            "visual": arch["visual"],
            "coupling": arch["coupling"],
            "cycles": arch["cycles"],
            "edges_weighted": arch["edges_weighted"],
            "fan_in": arch["fan_in"],
        }
        scores = builder.build_scores_from_arch(arch, int(result.get("score", 0)))
        scores["architecture"] = compute_architecture_score(arch)
        result["scores"] = scores

        result["clean_architecture"] = build_clean_architecture_report(root)

        # Contrato legado: score principal inalterado; flag útil para UI / SaaS
        result["ai_refactor_priority"] = int(result.get("score", 0)) < MIN_PASS_SCORE

        return result
