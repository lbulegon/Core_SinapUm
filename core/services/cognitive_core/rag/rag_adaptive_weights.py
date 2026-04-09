"""
Peso base por camada (namespace lógico). Ponto único para evoluir com tuning ou DB.
"""
from __future__ import annotations

from typing import Dict

_BASE: Dict[str, float] = {
    "tenant": 1.5,
    "operacional": 1.3,
    "global": 1.0,
}


def get_namespace_weight(source_type: str) -> float:
    st = str(source_type or "global").strip() or "global"
    return float(_BASE.get(st, 1.0))
