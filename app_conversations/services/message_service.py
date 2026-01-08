# ============================================================================
# ARQUITETURA NOVA - app_conversations.services.message_service
# ============================================================================

import logging
from typing import Dict, Any, Optional
from datetime import datetime
from django.utils import timezone
from ..models import Conversation, Message
from .conversation_service import ConversationService

logger = logging.getLogger(__name__)


class MessageService:
    """
    Service para gerenciar mensagens
    """
    
    @staticmethod
    def store_inbound(canonical_event: Dict[str, Any], conversation: Conversation) -> Message:
        """
        Armazena mensagem de entrada
        
        Args:
            canonical_event: Evento canônico
            conversation: Conversa à qual a mensagem pertence
        
        Returns:
            Message criada
        """
        # Parse timestamp
        timestamp_str = canonical_event.get('timestamp', '')
        if timestamp_str:
            try:
                timestamp = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
            except:
                timestamp = timezone.now()
        else:
            timestamp = timezone.now()
        
        # Mapear tipo de mensagem
        message_type_map = {
            'text': Message.MessageType.TEXT,
            'image': Message.MessageType.IMAGE,
            'audio': Message.MessageType.AUDIO,
            'video': Message.MessageType.VIDEO,
            'file': Message.MessageType.FILE,
            'interactive': Message.MessageType.INTERACTIVE,
        }
        message_type = message_type_map.get(
            canonical_event.get('message_type', 'text'),
            Message.MessageType.UNKNOWN
        )
        
        # Criar mensagem
        message = Message.objects.create(
            conversation=conversation,
            direction=Message.Direction.IN,
            message_type=message_type,
            text=canonical_event.get('text', ''),
            media_url=canonical_event.get('media'),
            provider=canonical_event.get('provider', 'evolution'),
            raw_payload=canonical_event.get('raw', {}),
            sent_by=Message.SentBy.CUSTOMER,
            timestamp=timestamp,
        )
        
        # Atualizar última mensagem da conversa
        ConversationService.update_last_message(conversation, timestamp)
        
        return message
    
    @staticmethod
    def store_outbound(
        conversation: Conversation,
        text: str,
        sent_by: str = Message.SentBy.SHOPPER,
        media_url: Optional[str] = None
    ) -> Message:
        """
        Armazena mensagem de saída
        
        Args:
            conversation: Conversa
            text: Texto da mensagem
            sent_by: Quem enviou (SHOPPER, AI, SYSTEM)
            media_url: URL da mídia (opcional)
        
        Returns:
            Message criada
        """
        message = Message.objects.create(
            conversation=conversation,
            direction=Message.Direction.OUT,
            message_type=Message.MessageType.TEXT if not media_url else Message.MessageType.IMAGE,
            text=text,
            media_url=media_url,
            provider='evolution',
            sent_by=sent_by,
            timestamp=timezone.now(),
        )
        
        # Atualizar última mensagem
        ConversationService.update_last_message(conversation)
        
        return message

