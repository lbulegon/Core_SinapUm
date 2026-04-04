"""
Pipeline de produto: envelope estável em torno do orquestrador.

A API HTTP do Core e o SaaS SinapLint esperam o **resultado interno** (dict do
``SinapLint``). Use :func:`run_analysis` para esse contrato; ``execute`` acrescenta
metadados para integrações que queiram ``status`` explícito.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from app_sinaplint.engine.orchestrator import SinapLintOrchestrator


class SinapPipeline:
    def execute_raw(self, path: Path | str | None = None) -> dict[str, Any]:
        return SinapLintOrchestrator().run(path)

    def execute(self, path: Path | str | None = None) -> dict[str, Any]:
        result = self.execute_raw(path)
        return {"status": "ok", "result": result}
