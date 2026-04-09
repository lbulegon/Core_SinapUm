"""
Orquestrador: tipo de evento → regras → dispatcher.
"""

from __future__ import annotations

import logging
from typing import Any, Dict, List

from core.cognition.chef_agno.dispatcher import emitir_comando
from core.cognition.chef_agno.rules import avaliar_pedido
from core.cognition.chef_agno.utils import criar_comando

logger = logging.getLogger("core_dispatch")


def processar_evento(evento: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Processa um evento canônico (ex.: vindo do webhook padronizado / ingestão).

    Retorna lista de resultados do HTTP client (um por comando emitido).
    """
    nome = (evento.get("evento") or evento.get("type") or "").strip()

    if nome == "pedido_recebido":
        decisao = avaliar_pedido(evento)
        return [_emit_safe(cmd) for cmd in decisao]

    if nome == "pedido_cancelado":
        cmd = criar_comando("cancelar_pedido", evento)
        return [_emit_safe(cmd)]

    logger.debug("chef_agno: evento não roteado: %s", nome)
    return []


def _emit_safe(comando: Dict[str, Any]) -> Dict[str, Any]:
    try:
        return emitir_comando(comando)
    except Exception as e:
        logger.exception("emitir_comando falhou: %s", e)
        return {"ok": False, "error": str(e), "command_id": comando.get("command_id")}
