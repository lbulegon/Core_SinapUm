"""
Signals - WhatsApp Canonical Events v1.0
=========================================

Signals para processar eventos canônicos.
"""
import logging
from django.dispatch import receiver
from .publisher import canonical_event_received
from .schemas import EventEnvelope

logger = logging.getLogger(__name__)


@receiver(canonical_event_received)
def handle_canonical_event(sender, envelope: EventEnvelope, event_log, **kwargs):
    """
    Handler para eventos canônicos recebidos
    
    Este signal é emitido quando um evento canônico é publicado.
    Pode ser usado para:
    - Processar mensagens no pipeline conversacional
    - Atualizar status de mensagens
    - Integrar com outros sistemas
    """
    try:
        logger.info(
            f"Evento canônico recebido via signal: {envelope.event_type.value} "
            f"from {envelope.from_number} (id: {envelope.event_id})"
        )
        
        # Aqui você pode adicionar lógica customizada:
        # - Processar mensagens no pipeline conversacional
        # - Atualizar status de mensagens
        # - Integrar com app_conversations, app_ai_bridge, etc.
        
        # Exemplo: Se for mensagem de texto, processar no pipeline
        if envelope.is_message_event() and envelope.from_number:
            # Integrar com pipeline conversacional existente
            # (não implementado aqui para manter aditivo)
            pass
        
    except Exception as e:
        logger.error(f"Erro ao processar evento canônico via signal: {e}", exc_info=True)
