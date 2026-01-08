"""
Publisher - WhatsApp Canonical Events v1.0
===========================================

Publica eventos canônicos: persiste em EventLog e emite signals.
"""
import logging
from datetime import datetime
from typing import Optional, Dict, Any
from django.db import transaction
from django.dispatch import Signal
from django.conf import settings

from .schemas import EventEnvelope
from .models import CanonicalEventLog

logger = logging.getLogger(__name__)

# Signal para eventos canônicos
canonical_event_received = Signal()


class EventPublisher:
    """
    Publisher de eventos canônicos
    
    Responsável por:
    - Persistir eventos em EventLog
    - Emitir signals para pipeline conversacional
    - Garantir idempotência
    """
    
    def publish(
        self,
        envelope: EventEnvelope,
        emit_signal: bool = True
    ) -> Optional[CanonicalEventLog]:
        """
        Publica evento canônico
        
        Args:
            envelope: EventEnvelope canônico
            emit_signal: Se True, emite signal (default: True)
        
        Returns:
            CanonicalEventLog criado ou None se já existir (idempotência)
        """
        # Verificar idempotência
        if envelope.provider_event_id:
            existing = CanonicalEventLog.objects.filter(
                provider_event_id=envelope.provider_event_id,
                event_source=envelope.event_source.value
            ).first()
            
            if existing:
                logger.debug(f"Evento já processado (idempotência): {envelope.provider_event_id}")
                return existing
        
        try:
            with transaction.atomic():
                # Criar log do evento
                event_log = CanonicalEventLog.objects.create(
                    event_id=envelope.event_id,
                    event_type=envelope.event_type.value,
                    event_source=envelope.event_source.value,
                    instance_key=envelope.instance_key,
                    timestamp=envelope.timestamp,
                    from_number=envelope.from_number,
                    to_number=envelope.to_number,
                    payload=envelope.payload.dict() if envelope.payload and hasattr(envelope.payload, 'dict') else envelope.payload,
                    message_id=envelope.message_id,
                    correlation_id=envelope.correlation_id,
                    shopper_id=envelope.shopper_id,
                    skm_id=envelope.skm_id,
                    raw_payload=envelope.raw,
                    provider_event_id=envelope.provider_event_id,
                    provider_message_id=envelope.provider_message_id,
                )
                
                # Emitir signal se habilitado
                if emit_signal:
                    try:
                        canonical_event_received.send(
                            sender=self.__class__,
                            envelope=envelope,
                            event_log=event_log
                        )
                        logger.debug(f"Signal emitido para evento {envelope.event_id}")
                    except Exception as e:
                        logger.error(f"Erro ao emitir signal: {e}", exc_info=True)
                
                logger.info(
                    f"Evento canônico publicado: {envelope.event_type.value} "
                    f"(id: {envelope.event_id}, source: {envelope.event_source.value})"
                )
                
                return event_log
        
        except Exception as e:
            logger.error(f"Erro ao publicar evento canônico: {e}", exc_info=True)
            return None
    
    def publish_batch(
        self,
        envelopes: list[EventEnvelope],
        emit_signal: bool = True
    ) -> list[CanonicalEventLog]:
        """
        Publica múltiplos eventos em batch
        
        Args:
            envelopes: Lista de EventEnvelope
            emit_signal: Se True, emite signals
        
        Returns:
            Lista de CanonicalEventLog criados
        """
        results = []
        for envelope in envelopes:
            result = self.publish(envelope, emit_signal=emit_signal)
            if result:
                results.append(result)
        return results


# Singleton
_publisher_instance: Optional[EventPublisher] = None


def get_event_publisher() -> EventPublisher:
    """Obtém instância singleton do publisher"""
    global _publisher_instance
    if _publisher_instance is None:
        _publisher_instance = EventPublisher()
    return _publisher_instance
