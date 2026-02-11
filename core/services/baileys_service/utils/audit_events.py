"""
Audit Events - Baileys Service
===============================

Sistema de auditoria de eventos do Baileys.
Equivalente ao auditEvents.js do projeto Node.js.
"""
import logging
from typing import Any, Dict

logger = logging.getLogger(__name__)


def audit_event(event_name: str, event_data: Dict[str, Any]):
    """
    Audita um evento do Baileys
    
    Args:
        event_name: Nome do evento
        event_data: Dados do evento
    """
    logger.debug(
        f"📡 Evento detectado: {event_name}",
        extra={
            'event_name': event_name,
            'event_data': event_data
        }
    )


def audit_connection_update(update: Dict[str, Any]):
    """Audita atualização de conexão"""
    connection = update.get('connection')
    last_disconnect = update.get('lastDisconnect')
    qr = update.get('qr')
    
    logger.info(
        f"📡 Atualização de Conexão: {connection}",
        extra={
            'connection': connection,
            'has_qr': qr is not None,
            'last_disconnect': last_disconnect
        }
    )


def audit_message_event(messages: list, event_type: str):
    """Audita evento de mensagem"""
    logger.debug(
        f"📡 Evento de Mensagem: {event_type}",
        extra={
            'event_type': event_type,
            'message_count': len(messages),
            'messages': messages
        }
    )


def audit_disconnect(reason: Any):
    """Audita desconexão"""
    logger.warning(
        "❌ Conexão encerrada",
        extra={
            'disconnect_reason': str(reason),
            'reason_type': type(reason).__name__
        }
    )
