"""
Models - WhatsApp Events
========================

Modelos para persistir eventos canônicos WhatsApp e gerenciar conversações/threads.
"""
import uuid
import hashlib
from django.db import models
from django.utils import timezone

# Django 3.1+ usa models.JSONField diretamente
JSONField = models.JSONField


class WhatsAppEventLog(models.Model):
    """
    Log de eventos canônicos WhatsApp
    
    Armazena todos os eventos normalizados para auditoria, roteamento e SKM Score.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # Identificação
    event_id = models.CharField(max_length=255, unique=True, db_index=True, help_text="ID único do evento")
    event_type = models.CharField(max_length=100, db_index=True, help_text="Tipo do evento canônico")
    event_version = models.CharField(max_length=10, default="1.0", help_text="Versão do schema")
    occurred_at = models.DateTimeField(db_index=True, help_text="Timestamp do evento")
    
    # Fonte (Provider)
    provider = models.CharField(max_length=50, db_index=True, help_text="Provider: evolution, cloud, baileys, etc.")
    provider_account_id = models.CharField(max_length=255, blank=True, null=True, help_text="ID da conta no provider")
    provider_message_id = models.CharField(max_length=255, blank=True, null=True, db_index=True, help_text="ID da mensagem no provider")
    webhook_id = models.CharField(max_length=255, blank=True, null=True, help_text="ID do webhook")
    
    # Idempotência
    idempotency_key = models.CharField(max_length=255, unique=True, db_index=True, help_text="Chave de idempotência (determinística)")
    correlation_id = models.CharField(max_length=255, blank=True, null=True, db_index=True, help_text="ID de correlação")
    parent_event_id = models.CharField(max_length=255, blank=True, null=True, db_index=True, help_text="ID do evento pai")
    
    # Roteamento
    shopper_id = models.CharField(max_length=255, blank=True, null=True, db_index=True, help_text="ID do shopper")
    skm_id = models.CharField(max_length=255, blank=True, null=True, db_index=True, help_text="ID do SKM (Sales Keeper Mesh)")
    keeper_id = models.CharField(max_length=255, blank=True, null=True, db_index=True, help_text="ID do keeper")
    conversation_id = models.CharField(max_length=255, blank=True, null=True, db_index=True, help_text="ID da conversação")
    thread_key = models.CharField(max_length=500, blank=True, null=True, db_index=True, help_text="Chave do thread (determinística)")
    
    # Ator
    actor_wa_id = models.CharField(max_length=50, blank=True, null=True, db_index=True, help_text="WhatsApp ID do ator")
    actor_role = models.CharField(max_length=50, blank=True, null=True, help_text="Role: customer, skm, shopper, keeper, system")
    
    # Contexto
    chat_type = models.CharField(max_length=20, blank=True, null=True, help_text="Tipo: private, group")
    group_id = models.CharField(max_length=255, blank=True, null=True, db_index=True, help_text="ID do grupo (se aplicável)")
    
    # Mensagem
    message_type = models.CharField(max_length=50, blank=True, null=True, help_text="Tipo: text, media, interactive, etc.")
    message_direction = models.CharField(max_length=20, blank=True, null=True, help_text="Direção: inbound, outbound")
    
    # Payloads
    payload_json = JSONField(default=dict, blank=True, help_text="Payload específico do evento (JSON)")
    raw_provider_payload = JSONField(default=dict, blank=True, help_text="Payload bruto do provider (JSON)")
    
    # Segurança
    signature_valid = models.BooleanField(default=True, help_text="Se assinatura é válida")
    risk_flags = JSONField(default=list, blank=True, help_text="Flags de risco")
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    processed_at = models.DateTimeField(null=True, blank=True, help_text="Timestamp de processamento")
    
    class Meta:
        db_table = 'app_whatsapp_events_eventlog'
        ordering = ['-occurred_at', '-created_at']
        indexes = [
            models.Index(fields=['idempotency_key']),  # Unique index
            models.Index(fields=['thread_key', '-occurred_at']),
            models.Index(fields=['provider_message_id']),
            models.Index(fields=['occurred_at']),
            models.Index(fields=['event_type', '-occurred_at']),
            models.Index(fields=['provider', '-occurred_at']),
            models.Index(fields=['conversation_id', '-occurred_at']),
            models.Index(fields=['shopper_id', '-occurred_at']),
            models.Index(fields=['skm_id', '-occurred_at']),
        ]
        verbose_name = 'WhatsApp Event Log'
        verbose_name_plural = 'WhatsApp Event Logs'
    
    def __str__(self):
        return f"{self.event_type} from {self.actor_wa_id} at {self.occurred_at}"


class WhatsAppConversation(models.Model):
    """
    Conversação WhatsApp
    
    Representa uma conversa/thread entre participantes.
    """
    STATUS_CHOICES = [
        ('open', 'Aberta'),
        ('closed', 'Fechada'),
        ('archived', 'Arquivada'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    conversation_id = models.CharField(max_length=255, unique=True, db_index=True, help_text="ID único da conversação")
    thread_key = models.CharField(max_length=500, unique=True, db_index=True, help_text="Chave do thread (determinística)")
    
    # Roteamento
    shopper_id = models.CharField(max_length=255, blank=True, null=True, db_index=True, help_text="ID do shopper")
    skm_id = models.CharField(max_length=255, blank=True, null=True, db_index=True, help_text="ID do SKM atribuído")
    keeper_id = models.CharField(max_length=255, blank=True, null=True, db_index=True, help_text="ID do keeper")
    
    # Status
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='open', db_index=True, help_text="Status da conversação")
    
    # Metadados
    last_event_at = models.DateTimeField(null=True, blank=True, db_index=True, help_text="Timestamp do último evento")
    last_actor_wa_id = models.CharField(max_length=50, blank=True, null=True, help_text="WhatsApp ID do último ator")
    tags = JSONField(default=list, blank=True, help_text="Tags da conversação")
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)
    closed_at = models.DateTimeField(null=True, blank=True, help_text="Timestamp de fechamento")
    
    class Meta:
        db_table = 'app_whatsapp_events_conversation'
        ordering = ['-last_event_at', '-created_at']
        indexes = [
            models.Index(fields=['thread_key']),  # Unique index
            models.Index(fields=['last_event_at']),
            models.Index(fields=['status', '-last_event_at']),
            models.Index(fields=['shopper_id', '-last_event_at']),
            models.Index(fields=['skm_id', '-last_event_at']),
        ]
        verbose_name = 'WhatsApp Conversation'
        verbose_name_plural = 'WhatsApp Conversations'
    
    def __str__(self):
        return f"Conversation {self.conversation_id} - Thread: {self.thread_key}"


class WhatsAppThreadParticipant(models.Model):
    """
    Participante de um thread/conversação
    
    Rastreia participantes e seus metadados.
    """
    ROLE_CHOICES = [
        ('customer', 'Cliente'),
        ('skm', 'SKM'),
        ('shopper', 'Shopper'),
        ('keeper', 'Keeper'),
        ('system', 'Sistema'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    conversation = models.ForeignKey(WhatsAppConversation, on_delete=models.CASCADE, related_name='participants', help_text="Conversação")
    wa_id = models.CharField(max_length=50, db_index=True, help_text="WhatsApp ID do participante")
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, db_index=True, help_text="Role do participante")
    display_name = models.CharField(max_length=255, blank=True, null=True, help_text="Nome de exibição")
    
    # Metadados
    first_seen_at = models.DateTimeField(auto_now_add=True, help_text="Primeira vez visto")
    last_seen_at = models.DateTimeField(auto_now=True, db_index=True, help_text="Última vez visto")
    is_blocked = models.BooleanField(default=False, help_text="Se está bloqueado")
    
    class Meta:
        db_table = 'app_whatsapp_events_threadparticipant'
        ordering = ['-last_seen_at']
        unique_together = [['conversation', 'wa_id']]
        indexes = [
            models.Index(fields=['conversation', 'wa_id']),
            models.Index(fields=['role', '-last_seen_at']),
        ]
        verbose_name = 'WhatsApp Thread Participant'
        verbose_name_plural = 'WhatsApp Thread Participants'
    
    def __str__(self):
        return f"{self.display_name or self.wa_id} ({self.role}) in {self.conversation.conversation_id}"


class WhatsAppMessageIndex(models.Model):
    """
    Índice de mensagens para performance
    
    Facilita busca rápida de mensagens por conversação.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    provider_message_id = models.CharField(max_length=255, unique=True, db_index=True, help_text="ID da mensagem no provider")
    message_id = models.UUIDField(db_index=True, help_text="ID interno da mensagem (event_id)")
    conversation = models.ForeignKey(WhatsAppConversation, on_delete=models.CASCADE, related_name='message_indexes', help_text="Conversação")
    
    # Metadados
    direction = models.CharField(max_length=20, db_index=True, help_text="Direção: inbound, outbound")
    message_type = models.CharField(max_length=50, db_index=True, help_text="Tipo: text, media, etc.")
    occurred_at = models.DateTimeField(db_index=True, help_text="Timestamp do evento")
    
    class Meta:
        db_table = 'app_whatsapp_events_messageindex'
        ordering = ['-occurred_at']
        indexes = [
            models.Index(fields=['provider_message_id']),  # Unique index
            models.Index(fields=['conversation', '-occurred_at']),
            models.Index(fields=['direction', '-occurred_at']),
        ]
        verbose_name = 'WhatsApp Message Index'
        verbose_name_plural = 'WhatsApp Message Indexes'
    
    def __str__(self):
        return f"Message {self.provider_message_id} in {self.conversation.conversation_id}"
