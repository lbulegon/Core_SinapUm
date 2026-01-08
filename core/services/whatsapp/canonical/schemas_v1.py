"""
Schemas - WhatsApp Canonical Events v1.0 (Completo)
===================================================

Schema completo do EventEnvelope v1.0 com todos os campos necessários
para roteamento, atribuição SKM, e integração com SKM Score.
"""
from datetime import datetime
from enum import Enum
from typing import Optional, Dict, Any, List, Union
from pydantic import BaseModel, Field, validator


class EventType(str, Enum):
    """Tipos de eventos canônicos WhatsApp v1.0"""
    # Mensagens
    MESSAGE_INBOUND = "whatsapp.message.inbound"
    MESSAGE_OUTBOUND = "whatsapp.message.outbound"
    MESSAGE_STATUS_QUEUED = "whatsapp.message.status.queued"
    MESSAGE_STATUS_SENT = "whatsapp.message.status.sent"
    MESSAGE_STATUS_DELIVERED = "whatsapp.message.status.delivered"
    MESSAGE_STATUS_READ = "whatsapp.message.status.read"
    MESSAGE_STATUS_FAILED = "whatsapp.message.status.failed"
    
    # Thread e Conversação
    THREAD_ASSIGNED = "whatsapp.thread.assigned"
    CONVERSATION_OPENED = "whatsapp.conversation.opened"
    CONVERSATION_CLOSED = "whatsapp.conversation.closed"
    
    # Grupo
    GROUP_JOINED = "whatsapp.group.joined"
    GROUP_LEFT = "whatsapp.group.left"
    
    # Commerce
    COMMERCE_INTENT_DETECTED = "commerce.intent.detected"
    COMMERCE_CART_CREATED = "commerce.cart.created"
    COMMERCE_ORDER_CREATED = "commerce.order.created"
    COMMERCE_PAYMENT_PENDING = "commerce.payment.pending"
    COMMERCE_PAYMENT_CONFIRMED = "commerce.payment.confirmed"
    COMMERCE_REFUND_REQUESTED = "commerce.refund.requested"
    COMMERCE_REFUND_COMPLETED = "commerce.refund.completed"
    COMMERCE_CHARGEBACK_OPENED = "commerce.chargeback.opened"
    COMMERCE_CHARGEBACK_WON = "commerce.chargeback.won"
    COMMERCE_CHARGEBACK_LOST = "commerce.chargeback.lost"
    
    # Delivery (AEP)
    DELIVERY_AREA_CREATED = "delivery.area.created"
    DELIVERY_LINK_SENT = "delivery.link.sent"
    DELIVERY_AREA_OPENED = "delivery.area.opened"
    DELIVERY_CONTENT_VIEWED = "delivery.content.viewed"
    DELIVERY_CONTENT_DOWNLOADED = "delivery.content.downloaded"
    DELIVERY_CONFIRMATION_RECEIVED = "delivery.confirmation.received"
    DELIVERY_ACCESS_REVOKED = "delivery.access.revoked"


class EventSource(BaseModel):
    """Fonte do evento (provider)"""
    provider: str = Field(..., description="Provider: evolution, cloud, baileys, simulated")
    provider_account_id: Optional[str] = Field(None, description="ID da conta no provider")
    provider_message_id: Optional[str] = Field(None, description="ID da mensagem no provider")
    webhook_id: Optional[str] = Field(None, description="ID do webhook (se aplicável)")


class Tenant(BaseModel):
    """Tenant/Projeto"""
    project: Optional[str] = Field(None, description="ID do projeto")
    env: Optional[str] = Field(None, description="Ambiente: dev, staging, prod")


class Routing(BaseModel):
    """Roteamento e atribuição"""
    shopper_id: Optional[str] = Field(None, description="ID do shopper")
    skm_id: Optional[str] = Field(None, description="ID do SKM (Sales Keeper Mesh)")
    keeper_id: Optional[str] = Field(None, description="ID do keeper")
    conversation_id: Optional[str] = Field(None, description="ID da conversação")
    thread_key: Optional[str] = Field(None, description="Chave do thread (determinística)")


class Actor(BaseModel):
    """Ator da mensagem/evento"""
    role: str = Field(..., description="Role: customer, skm, shopper, keeper, system")
    wa_id: str = Field(..., description="WhatsApp ID do ator")
    display_name: Optional[str] = Field(None, description="Nome de exibição")
    is_business: bool = Field(False, description="Se é conta business")


class Context(BaseModel):
    """Contexto da mensagem"""
    chat_type: str = Field(..., description="Tipo: private, group")
    group: Optional[Dict[str, Any]] = Field(None, description="Dados do grupo (se aplicável)")
    reply_to: Optional[str] = Field(None, description="ID da mensagem respondida")
    forwarded: Optional[Dict[str, Any]] = Field(None, description="Dados de encaminhamento")
    origin: Optional[str] = Field(None, description="Origem: entrypoint, mention, reaction, etc.")
    locale: Optional[str] = Field(None, description="Locale: pt-BR, en-US, etc.")


class MessageMedia(BaseModel):
    """Mídia da mensagem"""
    type: str = Field(..., description="Tipo: image, video, audio, document")
    url: Optional[str] = Field(None, description="URL da mídia")
    media_id: Optional[str] = Field(None, description="ID da mídia no provider")
    caption: Optional[str] = Field(None, description="Legenda")
    mime_type: Optional[str] = Field(None, description="Tipo MIME")
    file_size: Optional[int] = Field(None, description="Tamanho em bytes")
    file_name: Optional[str] = Field(None, description="Nome do arquivo")


class MessageInteractive(BaseModel):
    """Mensagem interativa (botões, listas)"""
    type: str = Field(..., description="Tipo: button, list")
    button_id: Optional[str] = Field(None, description="ID do botão clicado")
    list_id: Optional[str] = Field(None, description="ID da lista")
    selected_id: Optional[str] = Field(None, description="ID do item selecionado")


class Message(BaseModel):
    """Mensagem"""
    message_id: str = Field(..., description="ID único da mensagem")
    direction: str = Field(..., description="Direção: inbound, outbound")
    type: str = Field(..., description="Tipo: text, media, interactive, contact, location")
    text: Optional[str] = Field(None, description="Texto da mensagem")
    media: Optional[MessageMedia] = Field(None, description="Mídia (se aplicável)")
    interactive: Optional[MessageInteractive] = Field(None, description="Interativo (se aplicável)")
    contacts: Optional[List[Dict[str, Any]]] = Field(None, description="Contatos (se aplicável)")
    location: Optional[Dict[str, Any]] = Field(None, description="Localização (se aplicável)")


class Commerce(BaseModel):
    """Contexto de comércio"""
    intent: Optional[str] = Field(None, description="Intenção detectada")
    product_ref: Optional[str] = Field(None, description="Referência do produto")
    order_ref: Optional[str] = Field(None, description="Referência do pedido")
    price_context: Optional[Dict[str, Any]] = Field(None, description="Contexto de preço")


class Trace(BaseModel):
    """Rastreamento e correlação"""
    idempotency_key: str = Field(..., description="Chave de idempotência (determinística)")
    correlation_id: Optional[str] = Field(None, description="ID de correlação")
    parent_event_id: Optional[str] = Field(None, description="ID do evento pai")


class Security(BaseModel):
    """Segurança e risco"""
    signature_valid: bool = Field(True, description="Se assinatura é válida")
    risk_flags: List[str] = Field(default_factory=list, description="Flags de risco")


class EventEnvelope(BaseModel):
    """
    Envelope Canônico WhatsApp v1.0
    
    Padroniza eventos de diferentes providers em um formato único.
    """
    # Identificação
    event_id: str = Field(..., description="ID único do evento (UUID)")
    event_type: EventType = Field(..., description="Tipo do evento")
    event_version: str = Field(default="1.0", description="Versão do schema")
    occurred_at: datetime = Field(default_factory=datetime.now, description="Timestamp do evento")
    
    # Fonte
    source: EventSource = Field(..., description="Fonte do evento (provider)")
    
    # Tenant
    tenant: Optional[Tenant] = Field(None, description="Tenant/Projeto")
    
    # Roteamento
    routing: Optional[Routing] = Field(None, description="Roteamento e atribuição")
    
    # Ator
    actor: Optional[Actor] = Field(None, description="Ator da mensagem/evento")
    
    # Contexto
    context: Optional[Context] = Field(None, description="Contexto da mensagem")
    
    # Mensagem
    message: Optional[Message] = Field(None, description="Mensagem (se aplicável)")
    
    # Commerce
    commerce: Optional[Commerce] = Field(None, description="Contexto de comércio")
    
    # Rastreamento
    trace: Trace = Field(..., description="Rastreamento e correlação")
    
    # Segurança
    security: Security = Field(default_factory=lambda: Security(signature_valid=True), description="Segurança")
    
    # Raw payload
    raw: Dict[str, Any] = Field(default_factory=dict, description="Payload bruto do provider")
    
    class Config:
        use_enum_values = True
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
    
    @validator('event_id', pre=True, always=True)
    def generate_event_id(cls, v):
        """Gera event_id se não fornecido"""
        if not v:
            import uuid
            return str(uuid.uuid4())
        return v
    
    def to_dict(self) -> Dict[str, Any]:
        """Converte para dict (JSON serializable)"""
        return self.dict(exclude_none=True)
    
    def is_message_event(self) -> bool:
        """Verifica se é evento de mensagem"""
        return self.event_type.value.startswith("whatsapp.message")
    
    def is_status_event(self) -> bool:
        """Verifica se é evento de status"""
        return self.event_type.value.startswith("whatsapp.message.status")
    
    def is_commerce_event(self) -> bool:
        """Verifica se é evento de comércio"""
        return self.event_type.value.startswith("commerce")
    
    def is_delivery_event(self) -> bool:
        """Verifica se é evento de entrega"""
        return self.event_type.value.startswith("delivery")
