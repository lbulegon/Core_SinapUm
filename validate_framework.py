#!/usr/bin/env python3
"""
Gate de CI/CD: falha o processo se o score arquitetural estiver abaixo do limiar.

    python validate_framework.py

Exit codes: 0 = build OK, 1 = bloqueado (score < MIN_PASS_SCORE).
"""

from __future__ import annotations

import sys
from pathlib import Path

# Raiz = Core_SinapUm (pasta deste arquivo)
_ROOT = Path(__file__).resolve().parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from utils.framework_validator import MIN_PASS_SCORE, FrameworkValidator  # noqa: E402


def _persist_score(report) -> None:
    import os

    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "setup.settings")
    try:
        import django

        django.setup()
    except Exception as exc:
        print(f"Aviso: Django não inicializado — score não gravado na BD: {exc}", file=sys.stderr)
        return

    try:
        from services.architecture_score_service import persist_architecture_validation

        if persist_architecture_validation(report, min_pass_score=MIN_PASS_SCORE):
            print("Score persistido em ArchitectureScore (app_sinapcore).")
        else:
            print(
                "Aviso: score não persistido (BD indisponível, migrações ausentes ou erro ORM).",
                file=sys.stderr,
            )
    except Exception as exc:
        print(f"Aviso: falha ao persistir score na BD: {exc}", file=sys.stderr)


def main() -> int:
    report = FrameworkValidator(base_path=_ROOT).run()
    _persist_score(report)

    if report.score < MIN_PASS_SCORE:
        print(f"\nBUILD BLOQUEADO: score {report.score} < {MIN_PASS_SCORE} ({report.quality})")
        return 1
    print(f"\nBUILD OK (score {report.score}, {report.quality})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
