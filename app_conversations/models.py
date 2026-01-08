# ============================================================================
# ARQUITETURA NOVA - app_conversations
# ============================================================================
# Models para conversas, mensagens e sugestões de IA
# 
# ANTIGO: EvolutionMessage, WhatsAppMessageLog (Évora)
# NOVO: Conversation, Message, Suggestion (Core)
# ============================================================================

from django.db import models
from django.utils import timezone
import uuid


class Conversation(models.Model):
    """
    Conversa WhatsApp - Multi-tenant por shopper_id
    
    DIFERENÇA DO ANTIGO:
    - Antigo: Apenas mensagens individuais (EvolutionMessage)
    - Novo: Conversa como entidade com estado e contexto
    """
    
    class ChatType(models.TextChoices):
        PRIVATE = 'private', 'Privada'
        GROUP = 'group', 'Grupo'
    
    class Owner(models.TextChoices):
        AI = 'AI', 'IA'
        SHOPPER = 'SHOPPER', 'Shopper'
    
    class Mode(models.TextChoices):
        ASSISTIDO = 'assistido', 'Assistido'
        AUTO = 'auto', 'Automático'
    
    # Identificação
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    shopper_id = models.CharField(
        max_length=100,
        db_index=True,
        help_text="ID do Shopper (UUID do VitrineZap) - Multi-tenant"
    )
    instance_id = models.CharField(
        max_length=100,
        db_index=True,
        help_text="ID da instância Evolution (FK para app_whatsapp_gateway.EvolutionInstance)"
    )
    
    # Chave única da conversa
    conversation_key = models.CharField(
        max_length=200,
        db_index=True,
        help_text="Chave única da conversa (ex: 'whatsapp:+5511999999999' ou 'whatsapp_group:123')"
    )
    
    # Cliente
    customer_phone = models.CharField(
        max_length=20,
        db_index=True,
        help_text="Telefone do cliente (formato: +5511999999999)"
    )
    customer_name = models.CharField(
        max_length=200,
        blank=True,
        null=True,
        help_text="Nome do cliente (opcional)"
    )
    
    # Tipo e contexto
    chat_type = models.CharField(
        max_length=10,
        choices=ChatType.choices,
        default=ChatType.PRIVATE,
        help_text="Tipo de chat"
    )
    
    # Controle de IA
    owner = models.CharField(
        max_length=10,
        choices=Owner.choices,
        default=Owner.AI,
        help_text="Quem está gerenciando a conversa"
    )
    mode = models.CharField(
        max_length=10,
        choices=Mode.choices,
        default=Mode.ASSISTIDO,
        help_text="Modo de operação (IA sugere vs IA envia direto)"
    )
    
    # Tags e metadados
    tags = models.JSONField(
        default=list,
        blank=True,
        help_text="Tags da conversa (ex: ['venda', 'suporte'])"
    )
    
    # Timestamps
    last_message_at = models.DateTimeField(
        null=True,
        blank=True,
        db_index=True,
        help_text="Timestamp da última mensagem"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Conversa (Nova Arquitetura)'
        verbose_name_plural = 'Conversas (Nova Arquitetura)'
        ordering = ['-last_message_at', '-created_at']
        indexes = [
            models.Index(fields=['shopper_id', '-last_message_at']),
            models.Index(fields=['conversation_key']),
            models.Index(fields=['customer_phone', '-last_message_at']),
            models.Index(fields=['owner', 'mode']),
        ]
        unique_together = [['shopper_id', 'conversation_key']]
    
    def __str__(self):
        return f"{self.conversation_key} (Shopper: {self.shopper_id}) - {self.get_mode_display()}"


class Message(models.Model):
    """
    Mensagem normalizada - Multi-tenant
    
    DIFERENÇA DO ANTIGO:
    - Antigo: EvolutionMessage (formato Evolution API)
    - Novo: Message (formato normalizado/canônico)
    """
    
    class MessageType(models.TextChoices):
        TEXT = 'text', 'Texto'
        IMAGE = 'image', 'Imagem'
        AUDIO = 'audio', 'Áudio'
        VIDEO = 'video', 'Vídeo'
        FILE = 'file', 'Arquivo'
        INTERACTIVE = 'interactive', 'Interativo'
        UNKNOWN = 'unknown', 'Desconhecido'
    
    class Direction(models.TextChoices):
        IN = 'in', 'Entrada'
        OUT = 'out', 'Saída'
    
    class SentBy(models.TextChoices):
        CUSTOMER = 'customer', 'Cliente'
        AI = 'ai', 'IA'
        SHOPPER = 'shopper', 'Shopper'
        SYSTEM = 'system', 'Sistema'
    
    # Identificação
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    conversation = models.ForeignKey(
        Conversation,
        on_delete=models.CASCADE,
        related_name='messages',
        help_text="Conversa à qual a mensagem pertence"
    )
    
    # Direção e tipo
    direction = models.CharField(
        max_length=3,
        choices=Direction.choices,
        help_text="Direção da mensagem"
    )
    message_type = models.CharField(
        max_length=20,
        choices=MessageType.choices,
        default=MessageType.TEXT,
        help_text="Tipo de mensagem"
    )
    
    # Conteúdo
    text = models.TextField(
        blank=True,
        null=True,
        help_text="Texto da mensagem"
    )
    media_url = models.URLField(
        blank=True,
        null=True,
        help_text="URL da mídia (se houver)"
    )
    
    # Metadados
    provider = models.CharField(
        max_length=50,
        default='evolution',
        help_text="Provedor (ex: 'evolution')"
    )
    raw_payload = models.JSONField(
        default=dict,
        blank=True,
        help_text="Payload original do provedor"
    )
    
    # Quem enviou
    sent_by = models.CharField(
        max_length=10,
        choices=SentBy.choices,
        default=SentBy.CUSTOMER,
        help_text="Quem enviou a mensagem"
    )
    
    # Timestamp
    timestamp = models.DateTimeField(
        db_index=True,
        help_text="Timestamp da mensagem (do WhatsApp)"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'Mensagem (Nova Arquitetura)'
        verbose_name_plural = 'Mensagens (Nova Arquitetura)'
        ordering = ['timestamp', 'created_at']
        indexes = [
            models.Index(fields=['conversation', 'timestamp']),
            models.Index(fields=['direction', 'timestamp']),
            models.Index(fields=['sent_by', 'timestamp']),
        ]
    
    def __str__(self):
        direction_icon = "📥" if self.direction == self.Direction.IN else "📤"
        return f"{direction_icon} {self.conversation.conversation_key} - {self.message_type} - {self.timestamp}"


class Suggestion(models.Model):
    """
    Sugestão de resposta gerada pela IA
    
    NOVO: Não existe no código antigo
    """
    
    class Status(models.TextChoices):
        PENDING = 'pending', 'Pendente'
        SENT = 'sent', 'Enviada'
        DISMISSED = 'dismissed', 'Descartada'
    
    # Identificação
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    conversation = models.ForeignKey(
        Conversation,
        on_delete=models.CASCADE,
        related_name='suggestions',
        help_text="Conversa à qual a sugestão pertence"
    )
    
    # Análise da IA
    intent = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        help_text="Intenção detectada pela IA (ex: 'buscar_produto', 'fazer_pedido')"
    )
    confidence = models.FloatField(
        default=0.0,
        help_text="Confiança da IA (0.0 a 1.0)"
    )
    
    # Sugestão
    suggested_reply = models.TextField(
        help_text="Resposta sugerida pela IA"
    )
    
    # Ações sugeridas (JSON)
    actions = models.JSONField(
        default=list,
        blank=True,
        help_text="Ações sugeridas (ex: [{'tool': 'catalog.search', 'args': {...}}])"
    )
    
    # Status
    status = models.CharField(
        max_length=10,
        choices=Status.choices,
        default=Status.PENDING,
        db_index=True,
        help_text="Status da sugestão"
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    sent_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Quando a sugestão foi enviada (se status=sent)"
    )
    
    class Meta:
        verbose_name = 'Sugestão de IA'
        verbose_name_plural = 'Sugestões de IA'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['conversation', '-created_at']),
            models.Index(fields=['status', '-created_at']),
            models.Index(fields=['intent', '-created_at']),
        ]
    
    def __str__(self):
        status_icon = {
            'pending': '⏳',
            'sent': '✅',
            'dismissed': '❌'
        }.get(self.status, '❓')
        return f"{status_icon} {self.intent or 'N/A'} - {self.conversation.conversation_key} - {self.created_at}"

