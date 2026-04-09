"""
Compatibilidade: expõe `FrameworkValidator` e `ValidationReport` sobre o motor SinapLint.

Uso:

    python utils/framework_validator.py
    python validate_framework.py
"""

from __future__ import annotations

import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Optional, TextIO

# Garantir raiz Core_SinapUm no path quando se executa `python utils/framework_validator.py`
if str(Path(__file__).resolve().parent.parent) not in sys.path:
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app_sinaplint.engine import MIN_PASS_SCORE, SinapLint, run_analysis

# Reexport para scripts que importam `utils.framework_validator`
__all__ = ["MIN_PASS_SCORE", "FRAMEWORK_ROOT", "FrameworkValidator", "ValidationReport", "PENALTIES"]

# Raiz do framework = pasta pai de `utils/` (Core_SinapUm/)
FRAMEWORK_ROOT = Path(__file__).resolve().parent.parent

PENALTIES = {
    "missing_structure": 10,
    "bad_pattern": 15,
}


@dataclass
class ValidationReport:
    structure: list[tuple[str, bool]] = field(default_factory=list)
    files: list[tuple[str, bool]] = field(default_factory=list)
    structure_errors: list[tuple[str, str]] = field(default_factory=list)
    issues: list[tuple[str, str]] = field(default_factory=list)
    score: int = 100
    quality: str = "EXCELENTE"
    ok: bool = True
    sinaplint_raw: dict[str, Any] | None = None

    def merge_ok(self) -> None:
        self.ok = self.score >= MIN_PASS_SCORE


class FrameworkValidator:
    """Delega em `SinapLint` e preenche `ValidationReport` (persistência / CI legado)."""

    def __init__(self, base_path: Path | None = None) -> None:
        self.base_path = Path(base_path) if base_path is not None else FRAMEWORK_ROOT

    def run(self, stream: Optional[TextIO] = None) -> ValidationReport:
        out = stream or sys.stdout
        lint = run_analysis(self.base_path)

        report = ValidationReport()
        st = lint["structure"]
        report.structure = st.get("dirs_ok", [])
        report.files = st.get("files_ok", [])
        report.structure_errors = [("missing_structure", e) for e in st.get("errors", [])]
        report.issues = []
        for i in lint.get("pattern_issues", []):
            report.issues.append((i["path"], i["message"]))
        for i in lint.get("ast_issues", []):
            report.issues.append((i["path"], i["message"]))
        report.score = int(lint["score"])
        report.quality = str(lint["quality"])
        report.merge_ok()
        report.sinaplint_raw = lint

        out.write("Validação do framework Core_SinapUm (SinapLint)\n")
        out.write(f"Raiz: {self.base_path.resolve()}\n\n")

        out.write("Estrutura (diretórios obrigatórios)\n")
        for name, ok in report.structure:
            out.write(f"  [{'OK' if ok else 'FALTA'}] {name}\n")

        out.write("\nFicheiros obrigatórios\n")
        for name, ok in report.files:
            out.write(f"  [{'OK' if ok else 'FALTA'}] {name}\n")

        out.write("\nMódulos orbitais (PAOR)\n")
        for m in lint.get("modules", []):
            out.write(
                f"  {m['module']}: penalty={m['penalty']} missing={m.get('missing')}\n"
            )

        out.write("\nAnti-padrões (regex + AST)\n")
        if not report.issues:
            out.write("  Nenhum alerta nas heurísticas configuradas.\n")
        else:
            for path, msg in report.issues:
                out.write(f"  [!] {path} → {msg}\n")

        out.write("\n")
        out.write(f"Score arquitetural: {report.score}/100 ({report.quality})\n")
        out.write(f"Limiar mínimo para CI/deploy: {MIN_PASS_SCORE} (ACEITÁVEL)\n")
        out.write("\n")

        if report.structure_errors:
            out.write("Problemas de estrutura:\n")
            for kind, ident in report.structure_errors:
                out.write(f"  - [{kind}] {ident}\n")
            out.write("\n")

        if report.issues:
            out.write("Problemas de código:\n")
            for path, msg in report.issues:
                out.write(f"  - {path} → {msg}\n")
            out.write("\n")

        out.write("Resultado: " + ("PASS" if report.ok else "FAIL") + "\n")
        return report


def main() -> int:
    report = FrameworkValidator().run()
    return 0 if report.ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
