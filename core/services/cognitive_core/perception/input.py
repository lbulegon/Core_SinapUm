"""
Primeiridade (Signo): entrada unificada ao núcleo cognitivo.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, Optional


@dataclass
class PerceptionInput:
    """
    Signo operacional: tudo que o sistema "vê" num instante, antes da mediação.

    - raw_data: payload bruto (auditoria / replay)
    - normalized_data: forma canónica mínima para o pipeline
    """

    source: str
    raw_data: Dict[str, Any]
    normalized_data: Dict[str, Any]
    timestamp: datetime
    trace_id: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    @property
    def text(self) -> str:
        return str(self.normalized_data.get("text") or self.normalized_data.get("message") or "").strip()

    @property
    def channel(self) -> str:
        return str(self.normalized_data.get("channel") or self.metadata.get("channel") or "")

    @property
    def user_id(self) -> str:
        return str(
            self.normalized_data.get("user_id")
            or self.normalized_data.get("from")
            or self.metadata.get("user_id")
            or ""
        )

    @property
    def contract_version(self) -> str:
        return str(self.normalized_data.get("contract_version") or "v1")

    def context_hint(self) -> Dict[str, Any]:
        hint = self.normalized_data.get("context_hint")
        return hint if isinstance(hint, dict) else {}
