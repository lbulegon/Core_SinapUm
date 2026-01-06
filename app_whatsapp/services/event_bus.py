"""
Event Bus - Publica eventos canônicos (DB + logs)
"""
import logging
from typing import Dict, Any, Optional
from app_whatsapp.models import AppWhatsappEvent
from app_whatsapp.domain.events import create_canonical_event, EventType

logger = logging.getLogger(__name__)


class EventBus:
    """Publica eventos canônicos (DB + logs)"""
    
    @staticmethod
    def emit(
        provider: str,
        instance_key: str,
        event_type: EventType,
        data: Dict[str, Any],
        shopper_id: Optional[str] = None,
        correlation_id: Optional[str] = None,
    ) -> AppWhatsappEvent:
        """
        Emite evento canônico e persiste
        
        Args:
            provider: Nome do provider
            instance_key: Chave da instância
            event_type: Tipo do evento
            data: Dados do evento
            shopper_id: ID do shopper (opcional)
            correlation_id: ID de correlação (opcional)
        
        Returns:
            AppWhatsappEvent criado
        """
        event_payload = create_canonical_event(
            provider=provider,
            instance_key=instance_key,
            event_type=event_type,
            data=data,
            shopper_id=shopper_id,
            correlation_id=correlation_id,
        )
        
        # Persistir no DB
        event = AppWhatsappEvent.objects.create(
            event_id=event_payload["event_id"],
            provider=provider,
            instance_key=instance_key,
            type=event_type.value,
            shopper_id=shopper_id,
            correlation_id=correlation_id,
            data=event_payload["data"],
        )
        
        # Logar
        logger.info(
            f"[WhatsApp Gateway] Event: {event_type.value} | "
            f"Provider: {provider} | Instance: {instance_key} | "
            f"Shopper: {shopper_id} | Data: {data}"
        )
        
        return event
