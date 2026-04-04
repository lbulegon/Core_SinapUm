"""Penalização agregada dos módulos orbitais."""

from __future__ import annotations

from typing import Any


def total_module_penalty(modules: list[dict[str, Any]]) -> int:
    return sum(int(m.get("penalty", 0)) for m in modules)
