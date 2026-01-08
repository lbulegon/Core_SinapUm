# ============================================================================
# ARQUITETURA NOVA - app_conversations.services.conversation_service
# ============================================================================

import logging
from typing import Dict, Any, Optional
from django.utils import timezone
from ..models import Conversation

logger = logging.getLogger(__name__)


class ConversationService:
    """
    Service para gerenciar conversas
    """
    
    @staticmethod
    def get_or_create_by_inbound_event(canonical_event: Dict[str, Any]) -> tuple[Conversation, bool]:
        """
        Obtém ou cria conversa a partir de evento canônico
        
        Args:
            canonical_event: Evento canônico (do parser)
        
        Returns:
            (Conversation, created)
        """
        shopper_id = canonical_event.get('shopper_id')
        instance_id = canonical_event.get('instance_id')
        conversation_key = canonical_event.get('conversation_key')
        customer_phone = canonical_event.get('from_phone')
        chat_type = canonical_event.get('chat_type', 'private')
        
        if not all([shopper_id, instance_id, conversation_key, customer_phone]):
            raise ValueError("Campos obrigatórios faltando no evento canônico")
        
        conversation, created = Conversation.objects.get_or_create(
            shopper_id=shopper_id,
            conversation_key=conversation_key,
            defaults={
                'instance_id': instance_id,
                'customer_phone': customer_phone,
                'customer_name': None,  # Pode ser preenchido depois
                'chat_type': chat_type,
                'owner': Conversation.Owner.AI,
                'mode': Conversation.Mode.ASSISTIDO,
            }
        )
        
        return conversation, created
    
    @staticmethod
    def update_last_message(conversation: Conversation, timestamp: Optional[timezone.datetime] = None):
        """
        Atualiza timestamp da última mensagem
        
        Args:
            conversation: Conversa
            timestamp: Timestamp (opcional, usa now() se não fornecido)
        """
        conversation.last_message_at = timestamp or timezone.now()
        conversation.save()

