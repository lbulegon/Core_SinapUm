"""
Auto-correções conservadoras para padrões anti-framework (SinapLint fix).

As alterações são heurísticas: rever diff antes de commitar.
"""

from __future__ import annotations

import os
import re
from dataclasses import dataclass
from pathlib import Path

from sinaplint.path_utils import (
    SKIP_DIR_NAMES,
    path_ok_for_pattern_scan,
    restrict_framework_roots,
    should_skip_tree,
)

MARKER = "sinaplint-autofix"


@dataclass
class FixRecord:
    path: str
    description: str


def _iter_target_files(base: Path):
    """Mesmo âmbito que `pattern_rules` (núcleo do framework)."""
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
        if rel_parts and "sinaplint" in rel_parts:
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
            yield path, rel


def _apply_pause_orders(content: str) -> tuple[str, bool]:
    if f"# {MARKER}: usar fila" in content:
        return content, False
    if "pause_orders(" not in content:
        return content, False
    new = content.replace(
        "pause_orders(",
        f"# {MARKER}: usar fila SinapCoreCommand + handler\n# pause_orders(",
    )
    return new, new != content


def _apply_env_state(content: str) -> tuple[str, bool]:
    if f"# {MARKER}: env_state" in content:
        return content, False
    if not re.search(r"\bif\s+env_state\b", content):
        return content, False

    def repl(m: re.Match[str]) -> str:
        return (
            f"# {MARKER}: env_state — mover decisão para handler / comando\n"
            f"# {m.group(0)}"
        )

    new, n = re.subn(r"\bif\s+env_state\b", repl, content)
    return new, n > 0


class SinapFixer:
    """Aplica correções automáticas conservadoras em arquivos Python do âmbito SinapLint."""

    def __init__(self, base_path: Path) -> None:
        self.base_path = Path(base_path).resolve()

    def fix_files(self, *, dry_run: bool = False) -> list[FixRecord]:
        records: list[FixRecord] = []
        for path, rel in _iter_target_files(self.base_path):
            try:
                original = path.read_text(encoding="utf-8", errors="replace")
            except OSError:
                continue

            content = original

            content, did_po = _apply_pause_orders(content)
            if did_po:
                records.append(
                    FixRecord(
                        str(rel),
                        "Comentada chamada direta a pause_orders (rever e enfileirar comando)",
                    )
                )

            content, did_ev = _apply_env_state(content)
            if did_ev:
                records.append(
                    FixRecord(
                        str(rel),
                        "Comentada condição env_state (rever e mover para handler)",
                    )
                )

            if content == original:
                continue

            if dry_run:
                continue

            try:
                path.write_text(content, encoding="utf-8", newline="\n")
            except OSError:
                records.append(
                    FixRecord(str(rel), "ERRO: não foi possível gravar o arquivo")
                )

        return records
