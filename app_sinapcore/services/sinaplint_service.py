"""
Integração Django ↔ motor SinapLint (orquestrador + mesmo contrato JSON que o CLI).
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from app_sinaplint.engine import run_analysis


class SinapLintService:
    """Camada de serviço para views e tarefas que precisam do relatório completo."""

    def analyze(self, path: Path | str | None = None) -> dict[str, Any]:
        return run_analysis(path)
