# ============================================================================
# Contrato - Evento Canônico
# ============================================================================
# Definição do formato padronizado de eventos WhatsApp
# ============================================================================

from typing import Dict, Any, Optional
from dataclasses import dataclass
from datetime import datetime


@dataclass
class CanonicalEvent:
    """
    Evento Canônico - Formato padronizado de eventos WhatsApp
    
    Todos os eventos de diferentes provedores (Evolution, etc.) são
    convertidos para este formato antes de serem processados.
    """
    
    # Identificação multi-tenant
    tenant_id: Optional[str] = None
    shopper_id: Optional[str] = None
    instance_id: str = ''
    
    # Identificação da conversa
    conversation_id: Optional[str] = None
    conversation_key: str = ''  # ex: 'whatsapp:+5511999999999' ou 'whatsapp_group:123'
    
    # Remetente
    from_phone: str = ''
    
    # Tipo de chat
    chat_type: str = 'private'  # 'private' | 'group'
    
    # Mensagem
    message_type: str = 'text'  # 'text' | 'image' | 'audio' | 'video' | 'file' | 'interactive'
    text: str = ''
    media: Optional[str] = None  # URL da mídia
    
    # Timestamp
    timestamp: str = ''  # ISO format
    
    # Payload original
    raw: Dict[str, Any] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Converte para dict"""
        return {
            'tenant_id': self.tenant_id,
            'shopper_id': self.shopper_id,
            'instance_id': self.instance_id,
            'conversation_id': self.conversation_id,
            'conversation_key': self.conversation_key,
            'from_phone': self.from_phone,
            'chat_type': self.chat_type,
            'message_type': self.message_type,
            'text': self.text,
            'media': self.media,
            'timestamp': self.timestamp,
            'raw': self.raw or {},
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'CanonicalEvent':
        """Cria a partir de dict"""
        return cls(
            tenant_id=data.get('tenant_id'),
            shopper_id=data.get('shopper_id'),
            instance_id=data.get('instance_id', ''),
            conversation_id=data.get('conversation_id'),
            conversation_key=data.get('conversation_key', ''),
            from_phone=data.get('from_phone', ''),
            chat_type=data.get('chat_type', 'private'),
            message_type=data.get('message_type', 'text'),
            text=data.get('text', ''),
            media=data.get('media'),
            timestamp=data.get('timestamp', ''),
            raw=data.get('raw', {}),
        )

