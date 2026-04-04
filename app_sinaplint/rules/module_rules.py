"""
Verifica módulos orbitais em agent_core/modules/<nome>/ (arquivos PAOR).
"""

from __future__ import annotations

import os
from pathlib import Path

# PAOR completo: perceptor, analyzer, orchestrator, responder (+ module.py opcional)
REQUIRED_PAOR_FILES = (
    "perceptor.py",
    "analyzer.py",
    "orchestrator.py",
    "responder.py",
)


def check_modules(base: Path) -> list[dict]:
    results: list[dict] = []
    modules_path = base / "agent_core" / "modules"
    if not modules_path.is_dir():
        return [
            {
                "module": "(agent_core/modules)",
                "missing": list(REQUIRED_PAOR_FILES),
                "penalty": 25,
            }
        ]

    for name in sorted(os.listdir(modules_path)):
        module_path = modules_path / name
        if not module_path.is_dir() or name.startswith("_"):
            continue
        if name == "__pycache__":
            continue
        try:
            files = os.listdir(module_path)
        except OSError:
            continue
        missing = [f for f in REQUIRED_PAOR_FILES if f not in files]
        penalty = len(missing) * 5
        results.append(
            {
                "module": name,
                "missing": missing,
                "penalty": penalty,
            }
        )

    return results
