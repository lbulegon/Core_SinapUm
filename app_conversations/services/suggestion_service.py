# ============================================================================
# ARQUITETURA NOVA - app_conversations.services.suggestion_service
# ============================================================================

import logging
from typing import Dict, Any, Optional
from django.utils import timezone
from ..models import Conversation, Suggestion

logger = logging.getLogger(__name__)


class SuggestionService:
    """
    Service para gerenciar sugestões de IA
    """
    
    @staticmethod
    def create_from_ai(conversation: Conversation, ai_response: Dict[str, Any]) -> Suggestion:
        """
        Cria sugestão a partir de resposta da IA
        
        Args:
            conversation: Conversa
            ai_response: Resposta do OpenMind
                {
                    'intent': str,
                    'confidence': float,
                    'suggested_reply': str,
                    'actions': list (opcional)
                }
        
        Returns:
            Suggestion criada
        """
        suggestion = Suggestion.objects.create(
            conversation=conversation,
            intent=ai_response.get('intent'),
            confidence=ai_response.get('confidence', 0.0),
            suggested_reply=ai_response.get('suggested_reply', ''),
            actions=ai_response.get('actions', []),
            status=Suggestion.Status.PENDING,
        )
        
        return suggestion
    
    @staticmethod
    def mark_sent(suggestion_id: str) -> bool:
        """
        Marca sugestão como enviada
        
        Args:
            suggestion_id: ID da sugestão (UUID)
        
        Returns:
            True se marcada com sucesso
        """
        try:
            suggestion = Suggestion.objects.get(id=suggestion_id)
            suggestion.status = Suggestion.Status.SENT
            suggestion.sent_at = timezone.now()
            suggestion.save()
            return True
        except Suggestion.DoesNotExist:
            logger.warning(f"Sugestão {suggestion_id} não encontrada")
            return False
    
    @staticmethod
    def dismiss(suggestion_id: str) -> bool:
        """
        Descarta sugestão
        
        Args:
            suggestion_id: ID da sugestão
        
        Returns:
            True se descartada com sucesso
        """
        try:
            suggestion = Suggestion.objects.get(id=suggestion_id)
            suggestion.status = Suggestion.Status.DISMISSED
            suggestion.save()
            return True
        except Suggestion.DoesNotExist:
            logger.warning(f"Sugestão {suggestion_id} não encontrada")
            return False

