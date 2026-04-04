"""
Extrai nomes de módulo importados via AST (coerente com o resto do motor SinapLint).
"""

from __future__ import annotations

import ast
from pathlib import Path


class DependencyExtractor:
    def extract(self, file_path: Path) -> list[str]:
        """Lista de módulos referenciados (``import x`` e ``from x import``)."""
        try:
            src = Path(file_path).read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            return []
        try:
            tree = ast.parse(src, filename=str(file_path))
        except SyntaxError:
            return []
        out: list[str] = []
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    out.append(alias.name)
            elif isinstance(node, ast.ImportFrom) and node.module:
                # Imports relativos (``.``) omitidos aqui — resolução depende do pacote
                if getattr(node, "level", 0) and node.level > 0:
                    continue
                out.append(node.module)
        return out
