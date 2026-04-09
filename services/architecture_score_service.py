"""
Persistência do score do validador de framework em `ArchitectureScore` (ORM).
"""

from __future__ import annotations

import logging
from typing import Any

logger = logging.getLogger(__name__)


def persist_architecture_validation(
    report: Any,
    *,
    source: str = "validate_framework",
    min_pass_score: int = 80,
) -> bool:
    """
    Grava o resultado de `FrameworkValidator.run()` na BD.

    Devolve False se Django/BD não estiver disponível (ex.: CI sem Postgres),
    sem levantar exceção para o chamador.
    """
    try:
        from app_sinapcore.models.architecture_score import ArchitectureScore

        structure_errors = [
            [kind, ident] for kind, ident in getattr(report, "structure_errors", [])
        ]
        issues = [[p, m] for p, m in getattr(report, "issues", [])]

        sinaplint_payload = getattr(report, "sinaplint_raw", None)
        details: dict[str, Any] = {
            "structure_errors": structure_errors,
            "issues": issues,
        }
        if isinstance(sinaplint_payload, dict):
            details["sinaplint"] = sinaplint_payload

        ArchitectureScore.objects.create(
            score=int(getattr(report, "score", 0)),
            quality=str(getattr(report, "quality", ""))[:24],
            passed=bool(getattr(report, "ok", False)),
            min_pass_score=min_pass_score,
            details=details,
            source=source[:64],
        )
        return True
    except Exception:
        logger.warning("Não foi possível persistir ArchitectureScore", exc_info=True)
        return False
