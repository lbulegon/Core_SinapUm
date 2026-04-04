"""
Pacote ``engine``: orquestração, pipeline e motor SinapLint.

Compatível com imports antigos::

    from app_sinaplint.engine import SinapLint, MIN_PASS_SCORE, run_analysis
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from app_sinaplint.engine.context_builder import AnalysisContextBuilder
from app_sinaplint.engine.orchestrator import SinapLintOrchestrator
from app_sinaplint.engine.pipeline import SinapPipeline
from app_sinaplint.engine.sinap_lint import (
    MIN_PASS_SCORE,
    PENALTIES,
    SinapLint,
    quality_label,
)

__all__ = [
    "AnalysisContextBuilder",
    "MIN_PASS_SCORE",
    "PENALTIES",
    "SinapLint",
    "SinapLintOrchestrator",
    "SinapPipeline",
    "quality_label",
    "run_analysis",
]


def run_analysis(path: Path | str | None = None) -> dict[str, Any]:
    """
    Facade estável: inclui o mesmo núcleo que ``SinapLint().run()`` mais enriquecimento
    (``_context``, ``scores``, ``ai_refactor_priority``) via orquestrador.

    ``path`` — raiz do projeto a analisar; ``None`` = raiz do Core_SinapUm.
    """
    return SinapLintOrchestrator().run(path)
