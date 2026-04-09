"""
Montagem do payload de comando (contrato SinapUm ↔ MrFoo).
"""

from __future__ import annotations

import uuid
from typing import Any, Dict

from django.utils import timezone


def criar_comando(tipo: str, evento: Dict[str, Any], dados: Dict[str, Any] | None = None) -> Dict[str, Any]:
    """
    Gera dict pronto para `POST .../integracoes/sinapum/command/` no MrFoo.

    Espera em `evento`:
      - origem: { canal, externo_id }
      - event_id (ou id) para rastreio em contexto
    """
    origem = evento.get("origem") or {}
    canal = (origem.get("canal") or "").strip()
    externo_id = origem.get("externo_id")
    event_id = (
        evento.get("event_id")
        or evento.get("id")
        or evento.get("trace_id")
        or str(uuid.uuid4())
    )

    return {
        "command_id": str(uuid.uuid4()),
        "timestamp": timezone.now().isoformat(),
        "comando": tipo,
        "alvo": {
            "canal": canal,
            "externo_id": externo_id,
        },
        "dados": dict(dados or {}),
        "contexto": {
            "origem_evento": str(event_id),
        },
    }
