"""
Eventos canônicos do Creative Engine
"""
from enum import Enum
from typing import Dict, Any, Optional
from uuid import uuid4
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class CreativeEventType(str, Enum):
    """Tipos de eventos canônicos do Creative Engine"""
    CREATIVE_GENERATED = "CREATIVE_GENERATED"
    CREATIVE_VARIANT_GENERATED = "CREATIVE_VARIANT_GENERATED"
    CREATIVE_ADAPTED = "CREATIVE_ADAPTED"
    CREATIVE_SENT = "CREATIVE_SENT"
    CREATIVE_VIEWED = "CREATIVE_VIEWED"
    CREATIVE_RESPONDED = "CREATIVE_RESPONDED"
    CREATIVE_INTERESTED = "CREATIVE_INTERESTED"
    CREATIVE_ORDERED = "CREATIVE_ORDERED"
    CREATIVE_CONVERTED = "CREATIVE_CONVERTED"
    CREATIVE_IGNORED = "CREATIVE_IGNORED"


def create_creative_event(
    event_type: CreativeEventType,
    data: Dict[str, Any],
    shopper_id: Optional[str] = None,
    product_id: Optional[str] = None,
    creative_id: Optional[str] = None,
    variant_id: Optional[str] = None,
    correlation_id: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Cria payload canônico de evento do Creative Engine
    
    Args:
        event_type: Tipo do evento
        data: Dados do evento
        shopper_id: ID do shopper (opcional)
        product_id: ID do produto (opcional)
        creative_id: ID do criativo (opcional)
        variant_id: ID da variante (opcional)
        correlation_id: ID de correlação (opcional)
    
    Returns:
        Dict com estrutura canônica do evento
    """
    event = {
        "event_id": str(uuid4()),
        "ts": datetime.utcnow().isoformat() + "Z",
        "type": event_type.value,
        "shopper_id": shopper_id,
        "product_id": product_id,
        "creative_id": creative_id,
        "variant_id": variant_id,
        "correlation_id": correlation_id,
        "data": data,
    }
    
    # Logar evento
    logger.info(
        f"[Creative Engine] Event: {event_type.value} | "
        f"Shopper: {shopper_id} | Product: {product_id} | "
        f"Creative: {creative_id} | Variant: {variant_id} | "
        f"Data: {data}"
    )
    
    return event


def emit_creative_event(
    event_type: CreativeEventType,
    data: Dict[str, Any],
    shopper_id: Optional[str] = None,
    product_id: Optional[str] = None,
    creative_id: Optional[str] = None,
    variant_id: Optional[str] = None,
    correlation_id: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Emite evento canônico (wrapper para compatibilidade futura com EventBus)
    """
    return create_creative_event(
        event_type=event_type,
        data=data,
        shopper_id=shopper_id,
        product_id=product_id,
        creative_id=creative_id,
        variant_id=variant_id,
        correlation_id=correlation_id,
    )
