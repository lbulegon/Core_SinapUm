"""
Modo operacional global derivado do estado ambiental (IAmb / Redis).
"""

from __future__ import annotations

from typing import Any, Literal

SystemMode = Literal["NORMAL", "PRESSURE", "CRITICAL"]


def compute_mode_from_env_state(env_state: str | None) -> SystemMode:
    s = (env_state or "").strip().lower()
    if s == "colapso":
        return "CRITICAL"
    if s in ("sobrecarga", "pressao"):
        return "PRESSURE"
    return "NORMAL"


def compute_mode_from_env_dict(env: dict[str, Any] | None) -> SystemMode:
    if not env:
        return "NORMAL"
    return compute_mode_from_env_state(env.get("state"))
