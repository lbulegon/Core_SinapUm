"""
Schemas - WhatsApp Canonical Events v1.0
=========================================

Schemas Pydantic para eventos canônicos WhatsApp.
Padroniza eventos de diferentes providers (Evolution, Cloud API, Baileys, etc.).
"""
from datetime import datetime
from enum import Enum
from typing import Optional, Dict, Any, List, Union
from pydantic import BaseModel, Field, validator


class EventType(str, Enum):
    """Tipos de eventos canônicos WhatsApp"""
    # Mensagens
    MESSAGE_TEXT = "message.text"
    MESSAGE_MEDIA = "message.media"
    MESSAGE_LOCATION = "message.location"
    MESSAGE_CONTACT = "message.contact"
    MESSAGE_BUTTON = "message.button"
    MESSAGE_LIST = "message.list"
    
    # Status de mensagens
    MESSAGE_SENT = "message.sent"
    MESSAGE_DELIVERED = "message.delivered"
    MESSAGE_READ = "message.read"
    MESSAGE_FAILED = "message.failed"
    
    # Status de instância
    INSTANCE_CONNECTED = "instance.connected"
    INSTANCE_DISCONNECTED = "instance.disconnected"
    INSTANCE_QR_UPDATED = "instance.qr_updated"
    INSTANCE_CONNECTION_UPDATE = "instance.connection_update"
    
    # Webhooks genéricos
    WEBHOOK_RECEIVED = "webhook.received"
    WEBHOOK_ERROR = "webhook.error"


class EventSource(str, Enum):
    """Fonte do evento (provider)"""
    EVOLUTION = "evolution"
    CLOUD = "cloud"
    BAILEYS = "baileys"
    SIMULATED = "simulated"
    UNKNOWN = "unknown"


class MessagePayload(BaseModel):
    """Payload para mensagem de texto"""
    text: str = Field(..., description="Texto da mensagem")
    quoted_message_id: Optional[str] = Field(None, description="ID da mensagem citada")
    mentions: Optional[List[str]] = Field(None, description="Lista de números mencionados")


class MediaPayload(BaseModel):
    """Payload para mensagem de mídia"""
    media_type: str = Field(..., description="Tipo de mídia: image, video, audio, document")
    media_url: Optional[str] = Field(None, description="URL da mídia")
    media_id: Optional[str] = Field(None, description="ID da mídia no provider")
    caption: Optional[str] = Field(None, description="Legenda da mídia")
    mime_type: Optional[str] = Field(None, description="Tipo MIME")
    file_size: Optional[int] = Field(None, description="Tamanho do arquivo em bytes")
    file_name: Optional[str] = Field(None, description="Nome do arquivo")
    thumbnail_url: Optional[str] = Field(None, description="URL da miniatura")


class LocationPayload(BaseModel):
    """Payload para mensagem de localização"""
    latitude: float = Field(..., description="Latitude")
    longitude: float = Field(..., description="Longitude")
    name: Optional[str] = Field(None, description="Nome do local")
    address: Optional[str] = Field(None, description="Endereço do local")


class ContactPayload(BaseModel):
    """Payload para mensagem de contato"""
    name: Optional[str] = Field(None, description="Nome do contato")
    phone: Optional[str] = Field(None, description="Telefone do contato")
    vcard: Optional[str] = Field(None, description="vCard completo")


class ButtonPayload(BaseModel):
    """Payload para mensagem com botão"""
    button_id: str = Field(..., description="ID do botão clicado")
    button_text: Optional[str] = Field(None, description="Texto do botão")
    selected_button_id: Optional[str] = Field(None, description="ID do botão selecionado")


class ListPayload(BaseModel):
    """Payload para mensagem de lista"""
    list_id: Optional[str] = Field(None, description="ID da lista")
    selected_id: Optional[str] = Field(None, description="ID do item selecionado")
    selected_title: Optional[str] = Field(None, description="Título do item selecionado")
    selected_description: Optional[str] = Field(None, description="Descrição do item selecionado")


class StatusPayload(BaseModel):
    """Payload para status de mensagem"""
    status: str = Field(..., description="Status: sent, delivered, read, failed")
    message_id: str = Field(..., description="ID da mensagem")
    timestamp: Optional[datetime] = Field(None, description="Timestamp do status")
    error_code: Optional[str] = Field(None, description="Código de erro (se failed)")
    error_message: Optional[str] = Field(None, description="Mensagem de erro (se failed)")


class EventEnvelope(BaseModel):
    """
    Envelope canônico para eventos WhatsApp v1.0
    
    Padroniza eventos de diferentes providers em um formato único.
    """
    # Identificação
    event_id: str = Field(..., description="ID único do evento (UUID)")
    event_type: EventType = Field(..., description="Tipo do evento")
    event_source: EventSource = Field(..., description="Fonte do evento (provider)")
    
    # Contexto
    instance_key: str = Field(..., description="Chave da instância WhatsApp")
    timestamp: datetime = Field(default_factory=datetime.now, description="Timestamp do evento")
    
    # Origem/Destino
    from_number: Optional[str] = Field(None, description="Número de origem (remetente)")
    to_number: Optional[str] = Field(None, description="Número de destino")
    
    # Payload específico por tipo
    payload: Optional[Union[
        MessagePayload,
        MediaPayload,
        LocationPayload,
        ContactPayload,
        ButtonPayload,
        ListPayload,
        StatusPayload,
        Dict[str, Any]
    ]] = Field(None, description="Payload específico do evento")
    
    # Metadados
    message_id: Optional[str] = Field(None, description="ID da mensagem (se aplicável)")
    correlation_id: Optional[str] = Field(None, description="ID de correlação")
    shopper_id: Optional[str] = Field(None, description="ID do shopper (opcional)")
    skm_id: Optional[str] = Field(None, description="SKM ID (opcional)")
    
    # Raw payload do provider (para auditoria)
    raw: Dict[str, Any] = Field(default_factory=dict, description="Payload bruto do provider")
    
    # Idempotência
    provider_event_id: Optional[str] = Field(None, description="ID do evento no provider original")
    provider_message_id: Optional[str] = Field(None, description="ID da mensagem no provider")
    
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
        return self.event_type.value.startswith("message.")
    
    def is_status_event(self) -> bool:
        """Verifica se é evento de status"""
        return self.event_type.value.startswith("message.") and self.event_type in [
            EventType.MESSAGE_SENT,
            EventType.MESSAGE_DELIVERED,
            EventType.MESSAGE_READ,
            EventType.MESSAGE_FAILED,
        ]
