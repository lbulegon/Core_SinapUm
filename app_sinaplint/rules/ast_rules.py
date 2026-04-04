"""
Análise AST: chamadas diretas e nomes suspeitos (com exclusões).
"""

from __future__ import annotations

import ast
import os
from pathlib import Path

from app_sinaplint.path_utils import (
    SKIP_DIR_NAMES,
    path_ok_for_pattern_scan,
    restrict_framework_roots,
    should_skip_tree,
)


def _call_name(node: ast.Call) -> str | None:
    if isinstance(node.func, ast.Name):
        return node.func.id
    if isinstance(node.func, ast.Attribute) and isinstance(node.func.value, ast.Name):
        return node.func.attr
    return None


def _if_test_names(node: ast.AST) -> list[str]:
    """Nomes referenciados na condição de um if (heurística)."""
    names: list[str] = []
    if isinstance(node, ast.Name):
        names.append(node.id)
    elif isinstance(node, ast.Compare) and isinstance(node.left, ast.Name):
        names.append(node.left.id)
    return names


def check_ast(base: Path) -> list[dict[str, str]]:
    issues: list[dict[str, str]] = []

    for root, dirs, files in os.walk(base, topdown=True):
        root_path = Path(root)
        try:
            rel_parts = root_path.relative_to(base).parts
        except ValueError:
            rel_parts = ()

        dirs[:] = [d for d in sorted(dirs) if d not in SKIP_DIR_NAMES]
        if should_skip_tree(rel_parts):
            dirs[:] = []
            continue
        if rel_parts and not restrict_framework_roots(rel_parts):
            if rel_parts[0] == "services" and len(rel_parts) == 1:
                dirs[:] = []
            elif rel_parts[0] == "services" and len(rel_parts) > 1:
                dirs[:] = []
                continue
            else:
                dirs[:] = []
                continue

        for file in files:
            if not file.endswith(".py"):
                continue
            path = root_path / file
            rel = path.relative_to(base)
            if not path_ok_for_pattern_scan(rel):
                continue
            try:
                src = path.read_text(encoding="utf-8", errors="replace")
                tree = ast.parse(src, filename=str(rel))
            except (OSError, SyntaxError):
                continue

            for node in ast.walk(tree):
                if isinstance(node, ast.Call):
                    cid = _call_name(node)
                    if cid == "pause_orders":
                        issues.append(
                            {
                                "path": str(rel),
                                "message": "Chamada AST a pause_orders (usar fila/handler)",
                            }
                        )
                if isinstance(node, ast.If):
                    for n in _if_test_names(node.test):
                        if n == "env_state":
                            issues.append(
                                {
                                    "path": str(rel),
                                    "message": "Condição sobre env_state (evitar decisão hardcoded)",
                                }
                            )

    return issues
