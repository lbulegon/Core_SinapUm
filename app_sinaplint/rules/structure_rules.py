"""Validação de diretórios e arquivos obrigatórios do framework."""

from __future__ import annotations

from pathlib import Path

REQUIRED_DIRS = [
    "agent_core",
    "command_engine",
    "services",
    "models",
    "views",
]

REQUIRED_FILES = [
    "command_engine/executor.py",
    "command_engine/registry.py",
    "command_engine/bootstrap.py",
    "agent_core/core/agent.py",
    "agent_core/core/engine.py",
    "agent_core/core/interfaces.py",
]


def check_structure(base: Path) -> dict:
    """
    Devolve erros de estrutura e listas de verificação para relatório.
    """
    dirs_ok: list[tuple[str, bool]] = []
    files_ok: list[tuple[str, bool]] = []
    errors: list[str] = []

    for d in REQUIRED_DIRS:
        ok = (base / d).is_dir()
        dirs_ok.append((d, ok))
        if not ok:
            errors.append(f"dir:{d}")

    for rel in REQUIRED_FILES:
        ok = (base / rel).is_file()
        files_ok.append((rel, ok))
        if not ok:
            errors.append(f"file:{rel}")

    return {
        "dirs_ok": dirs_ok,
        "files_ok": files_ok,
        "errors": errors,
    }
