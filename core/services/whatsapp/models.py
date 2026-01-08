"""
Models - WhatsApp Gateway
==========================

Models para providers que precisam persistir dados (ex: SimulatedMessage).
"""
import uuid
from django.db import models


class SimulatedMessage(models.Model):
    """
    Model para armazenar mensagens simuladas
    
    NOTA: Esta tabela só é criada se usar provider 'simulated'.
    Não interfere com modelos existentes.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    to = models.CharField(max_length=20, db_index=True)
    text = models.TextField(blank=True)
    media_url = models.URLField(blank=True, null=True)
    caption = models.TextField(blank=True)
    message_type = models.CharField(max_length=20, default='text')
    metadata = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    
    class Meta:
        db_table = 'core_whatsapp_simulated_message'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['to', '-created_at']),
        ]
        verbose_name = 'Mensagem Simulada'
        verbose_name_plural = 'Mensagens Simuladas'
    
    def __str__(self):
        return f"Simulated {self.message_type} to {self.to} at {self.created_at}"
