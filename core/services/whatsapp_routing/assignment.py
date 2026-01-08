"""
Assignment Policy - Atribuição SKM
===================================

Políticas de atribuição de SKM para threads/conversações.
"""
import logging
from typing import Optional, Dict, Any
from django.conf import settings

from core.services.whatsapp.canonical.schemas_v1 import EventEnvelope
from app_whatsapp_events.models import WhatsAppConversation

logger = logging.getLogger(__name__)


class AssignmentPolicy:
    """Política base de atribuição"""
    
    def assign_for_group(
        self,
        envelope: EventEnvelope,
        conversation: Optional[WhatsAppConversation] = None
    ) -> Optional[str]:
        """
        Atribui SKM para grupo
        
        Args:
            envelope: EventEnvelope
            conversation: WhatsAppConversation (opcional)
        
        Returns:
            skm_id atribuído ou None
        """
        return None


class DefaultAssignmentPolicy(AssignmentPolicy):
    """Política padrão: mantém SKM existente ou atribui padrão do shopper"""
    
    def assign_for_group(
        self,
        envelope: EventEnvelope,
        conversation: Optional[WhatsAppConversation] = None
    ) -> Optional[str]:
        """Atribui SKM padrão do shopper"""
        if isinstance(envelope, dict):
            routing = envelope.get('routing') or {}
        else:
            routing = envelope.routing.dict() if envelope.routing else {}
        
        shopper_id = routing.get('shopper_id')
        
        if shopper_id:
            # TODO: Implementar lógica de SKM padrão do shopper
            # Por enquanto, retornar None
            return None
        
        return None


class RoundRobinAssignmentPolicy(AssignmentPolicy):
    """Política round-robin: distribui entre SKMs disponíveis"""
    
    def assign_for_group(
        self,
        envelope: EventEnvelope,
        conversation: Optional[WhatsAppConversation] = None
    ) -> Optional[str]:
        """Atribui usando round-robin"""
        if isinstance(envelope, dict):
            routing = envelope.get('routing') or {}
        else:
            routing = envelope.routing.dict() if envelope.routing else {}
        
        shopper_id = routing.get('shopper_id')
        
        if not shopper_id:
            return None
        
        # TODO: Implementar lógica de round-robin
        # Por enquanto, retornar None
        return None


class StickyAssignmentPolicy(AssignmentPolicy):
    """Política sticky: mantém mesmo SKM que já interagiu"""
    
    def assign_for_group(
        self,
        envelope: EventEnvelope,
        conversation: Optional[WhatsAppConversation] = None
    ) -> Optional[str]:
        """Mantém SKM que já interagiu no grupo"""
        if conversation:
            # Verificar último SKM ativo no grupo
            # TODO: Implementar lógica de last_active_skm
            pass
        
        return None


# Factory
_policy_instances: Dict[str, AssignmentPolicy] = {}


def get_assignment_policy(policy_name: str = 'default') -> AssignmentPolicy:
    """Obtém instância da política de atribuição"""
    if policy_name not in _policy_instances:
        if policy_name == 'round_robin':
            _policy_instances[policy_name] = RoundRobinAssignmentPolicy()
        elif policy_name == 'sticky':
            _policy_instances[policy_name] = StickyAssignmentPolicy()
        else:
            _policy_instances[policy_name] = DefaultAssignmentPolicy()
    
    return _policy_instances[policy_name]
