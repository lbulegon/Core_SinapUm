"""
Heurísticas textuais + sugestões de melhoria (sem AST).
"""

from __future__ import annotations

import os
import re
from pathlib import Path

from app_sinaplint.path_utils import (
    SKIP_DIR_NAMES,
    path_ok_for_pattern_scan,
    restrict_framework_roots,
    should_skip_tree,
)


def _regex_pause_orders() -> re.Pattern[str]:
    return re.compile(r"\bpause_orders\s*\(")


def check_patterns(base: Path) -> dict:
    """
    Deteta anti-padrões por regex no núcleo do framework.
    Devolve issues [{path, message}] e suggestions estáticas.
    """
    issues: list[dict[str, str]] = []
    rx = _regex_pause_orders()

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
                content = path.read_text(encoding="utf-8", errors="replace")
            except OSError:
                continue
            if rx.search(content):
                issues.append(
                    {
                        "path": str(rel),
                        "message": "Possível chamada direta a pause_orders (preferir fila + handler)",
                    }
                )

    suggestions = [
        {
            "problem": "Chamada direta a comando operacional",
            "suggestion": "Enfileirar SinapCoreCommand e executar via handler em command_engine/handlers",
        },
        {
            "problem": "Lógica de decisão em view ou string mágica",
            "suggestion": "Mover regra para agent_core/modules e emitir comando nomeado",
        },
    ]

    return {"issues": issues, "suggestions": suggestions}
