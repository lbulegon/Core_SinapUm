"""Defaults de módulos cognitivos (sem Django)."""

from __future__ import annotations

from typing import Any

MODULE_DEFAULTS: dict[str, dict[str, Any]] = {
    "environmental": {
        "enabled": True,
        "priority": 10,
    },
    "cognitive": {
        "enabled": False,
        "priority": 20,
    },
}
