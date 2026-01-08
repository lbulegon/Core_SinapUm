# ============================================================================
# ARQUITETURA NOVA - app_whatsapp_gateway
# ============================================================================
# Models para instâncias Evolution multi-tenant por shopper_id
# 
# ANTIGO: EvolutionInstance (Évora) - instância única
# NOVO: EvolutionInstance (Core) - multi-tenant por shopper_id
# ============================================================================

from django.db import models
from django.utils import timezone
import uuid


class EvolutionInstance(models.Model):
    """
    Instância Evolution API - Multi-tenant por shopper_id
    
    DIFERENÇA DO ANTIGO:
    - Antigo (Évora): Instância única para todo o sistema
    - Novo (Core): Uma instância por shopper_id (multi-tenant)
    """
    
    class InstanceStatus(models.TextChoices):
        CREATING = 'creating', 'Criando'
        OPENING = 'opening', 'Abrindo'
        OPEN = 'open', 'Conectada'
        CLOSE = 'close', 'Desconectada'
        CONNECTING = 'connecting', 'Conectando'
        UNPAIRED = 'unpaired', 'Não pareado'
        UNPAIRED_IDLE = 'unpaired_idle', 'Não pareado (ocioso)'
        UNKNOWN = 'unknown', 'Desconhecido'
    
    # Identificação multi-tenant
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    shopper_id = models.CharField(
        max_length=100,
        db_index=True,
        help_text="ID do Shopper (UUID do VitrineZap) - Multi-tenant"
    )
    instance_id = models.CharField(
        max_length=100,
        unique=True,
        db_index=True,
        help_text="ID da instância na Evolution API (ex: 'shopper_123')"
    )
    
    # Status
    status = models.CharField(
        max_length=20,
        choices=InstanceStatus.choices,
        default=InstanceStatus.UNKNOWN,
        help_text="Status atual da instância"
    )
    
    # QR Code
    qrcode = models.TextField(
        blank=True,
        null=True,
        help_text="QR Code para conectar (base64)"
    )
    qrcode_url = models.URLField(
        blank=True,
        null=True,
        help_text="URL do QR Code"
    )
    
    # Informações do WhatsApp conectado
    phone_number = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        help_text="Número de telefone conectado"
    )
    phone_name = models.CharField(
        max_length=200,
        blank=True,
        null=True,
        help_text="Nome do WhatsApp conectado"
    )
    
    # Configurações
    is_active = models.BooleanField(
        default=True,
        help_text="Instância está ativa e sendo usada"
    )
    
    # Metadados
    last_sync = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Última sincronização com Evolution API"
    )
    metadata = models.JSONField(
        default=dict,
        blank=True,
        help_text="Metadados adicionais da instância"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Instância Evolution (Nova Arquitetura)'
        verbose_name_plural = 'Instâncias Evolution (Nova Arquitetura)'
        ordering = ['-is_active', '-created_at']
        indexes = [
            models.Index(fields=['shopper_id', 'status']),
            models.Index(fields=['instance_id']),
            models.Index(fields=['is_active', '-created_at']),
        ]
        unique_together = [['shopper_id', 'instance_id']]
    
    def __str__(self):
        status_icon = "✅" if self.status == self.InstanceStatus.OPEN else "❌"
        return f"{status_icon} {self.instance_id} (Shopper: {self.shopper_id}) - {self.get_status_display()}"


class WebhookEvent(models.Model):
    """
    Log de eventos recebidos da Evolution API
    
    Armazena todos os webhooks recebidos para auditoria e debug.
    """
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    instance = models.ForeignKey(
        EvolutionInstance,
        on_delete=models.CASCADE,
        related_name='webhook_events',
        help_text="Instância que recebeu o evento"
    )
    
    event_type = models.CharField(
        max_length=50,
        db_index=True,
        help_text="Tipo de evento (ex: 'messages.upsert', 'qrcode.updated')"
    )
    
    raw_payload = models.JSONField(
        help_text="Payload completo recebido da Evolution API"
    )
    
    processed = models.BooleanField(
        default=False,
        db_index=True,
        help_text="Evento foi processado"
    )
    
    error_message = models.TextField(
        blank=True,
        null=True,
        help_text="Mensagem de erro se processamento falhou"
    )
    
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    
    class Meta:
        verbose_name = 'Evento Webhook Evolution'
        verbose_name_plural = 'Eventos Webhook Evolution'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['instance', '-created_at']),
            models.Index(fields=['event_type', '-created_at']),
            models.Index(fields=['processed', '-created_at']),
        ]
    
    def __str__(self):
        return f"{self.event_type} - {self.instance.instance_id} - {self.created_at}"

