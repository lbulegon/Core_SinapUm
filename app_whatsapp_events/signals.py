"""
Signals - WhatsApp Events
"""
import logging
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import WhatsAppEventLog, WhatsAppConversation

logger = logging.getLogger(__name__)


@receiver(post_save, sender=WhatsAppEventLog)
def handle_event_log_created(sender, instance, created, **kwargs):
    """Handler para quando um evento é criado"""
    if created:
        logger.debug(f"Evento criado: {instance.event_id} (type: {instance.event_type})")
        
        # Aqui você pode adicionar lógica customizada:
        # - Processar eventos no pipeline conversacional
        # - Atualizar métricas
        # - Integrar com SKM Score
        # etc.
