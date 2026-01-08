"""
Models - WhatsApp Canonical Events v1.0
=======================================

Models para persistir eventos canônicos.
"""
import uuid
from django.db import models
from django.utils import timezone
try:
    from django.contrib.postgres.fields import JSONField
except ImportError:
    # Django 3.1+ usa models.JSONField diretamente
    from django.db import models
    JSONField = models.JSONField


class CanonicalEventLog(models.Model):
    """
    Log de eventos canônicos WhatsApp
    
    Armazena todos os eventos normalizados para auditoria e processamento.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # Identificação
    event_id = models.CharField(max_length=255, unique=True, db_index=True, help_text="ID único do evento")
    event_type = models.CharField(max_length=50, db_index=True, help_text="Tipo do evento canônico")
    event_source = models.CharField(max_length=50, db_index=True, help_text="Fonte do evento (provider)")
    
    # Contexto
    instance_key = models.CharField(max_length=255, db_index=True, help_text="Chave da instância WhatsApp")
    timestamp = models.DateTimeField(db_index=True, help_text="Timestamp do evento")
    
    # Origem/Destino
    from_number = models.CharField(max_length=20, blank=True, null=True, db_index=True, help_text="Número de origem")
    to_number = models.CharField(max_length=20, blank=True, null=True, db_index=True, help_text="Número de destino")
    
    # Payload
    payload = JSONField(default=dict, blank=True, help_text="Payload específico do evento")
    
    # Metadados
    message_id = models.CharField(max_length=255, blank=True, null=True, db_index=True, help_text="ID da mensagem")
    correlation_id = models.CharField(max_length=255, blank=True, null=True, db_index=True, help_text="ID de correlação")
    shopper_id = models.CharField(max_length=255, blank=True, null=True, db_index=True, help_text="ID do shopper")
    skm_id = models.CharField(max_length=255, blank=True, null=True, db_index=True, help_text="SKM ID")
    
    # Raw payload do provider
    raw_payload = JSONField(default=dict, blank=True, help_text="Payload bruto do provider")
    
    # Idempotência
    provider_event_id = models.CharField(max_length=255, blank=True, null=True, db_index=True, help_text="ID do evento no provider")
    provider_message_id = models.CharField(max_length=255, blank=True, null=True, db_index=True, help_text="ID da mensagem no provider")
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    processed_at = models.DateTimeField(null=True, blank=True, help_text="Timestamp de processamento")
    
    class Meta:
        db_table = 'core_whatsapp_canonical_event_log'
        ordering = ['-timestamp', '-created_at']
        indexes = [
            models.Index(fields=['event_type', '-timestamp']),
            models.Index(fields=['event_source', '-timestamp']),
            models.Index(fields=['instance_key', '-timestamp']),
            models.Index(fields=['from_number', '-timestamp']),
            models.Index(fields=['shopper_id', '-timestamp']),
            models.Index(fields=['provider_event_id']),
            models.Index(fields=['provider_message_id']),
        ]
        verbose_name = 'Evento Canônico WhatsApp'
        verbose_name_plural = 'Eventos Canônicos WhatsApp'
    
    def __str__(self):
        return f"{self.event_type} from {self.from_number} at {self.timestamp}"
