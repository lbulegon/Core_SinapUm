from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any


@dataclass
class PricingContext:
    """
    Contexto agregado para precificação (Core + domínio MrFoo via AGNO_*_MODEL).

    Valores de demanda/tempo/operacional são normalizados em [0, 1] quando aplicável.
    """

    produto_id: int
    preco_base: float
    demanda: float
    tempo: float
    operacional: float
    canal: str = "app"
    timestamp: datetime | None = None
    empresa_id: int | None = None
    metadata: dict[str, Any] = field(default_factory=dict)
