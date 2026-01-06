"""
Eventos canônicos do WhatsApp Gateway
"""
from enum import Enum
from typing import Dict, Any, Optional
from uuid import uuid4
from django.utils import timezone


class EventType(str, Enum):
    """Tipos de eventos canônicos"""
    INSTANCE_CREATED = "INSTANCE_CREATED"
    QR_UPDATED = "QR_UPDATED"
    CONNECTED = "CONNECTED"
    DISCONNECTED = "DISCONNECTED"
    MESSAGE_IN = "MESSAGE_IN"
    MESSAGE_OUT = "MESSAGE_OUT"
    DELIVERY = "DELIVERY"
    ERROR = "ERROR"


def create_canonical_event(
    provider: str,
    instance_key: str,
    event_type: EventType,
    data: Dict[str, Any],
    shopper_id: Optional[str] = None,
    correlation_id: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Cria payload canônico de evento
    
    Args:
        provider: Nome do provider (simulated, cloud, baileys, evolution)
        instance_key: Chave da instância
        event_type: Tipo do evento
        data: Dados do evento
        shopper_id: ID do shopper (opcional)
        correlation_id: ID de correlação (opcional)
    
    Returns:
        Dict com estrutura canônica do evento
    """
    return {
        "event_id": str(uuid4()),
        "ts": timezone.now().isoformat(),
        "provider": provider,
        "instance_key": instance_key,
        "type": event_type.value,
        "shopper_id": shopper_id,
        "correlation_id": correlation_id,
        "data": data,
    }
