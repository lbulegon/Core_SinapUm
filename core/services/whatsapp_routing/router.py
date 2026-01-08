"""
Router - WhatsApp Routing
=========================

Serviço de roteamento para mensagens WhatsApp com suporte a grupos e atribuição SKM.

INTEGRAÇÃO COM ROLLOUT MANAGER:
- Usa feature flags para controle gradual de roteamento
- Suporta rollout por shopper_id (allowlist, denylist, percent)
"""
import logging
from typing import Optional, Dict, Any
from django.conf import settings

from core.services.whatsapp.canonical.schemas_v1 import EventEnvelope
from app_whatsapp_events.utils import (
    generate_thread_key,
    get_or_create_conversation,
    append_event,
)
from app_whatsapp_events.models import WhatsAppConversation

# Importar rollout manager
try:
    from core.services.feature_flags.rollout import get_rollout_manager
    from core.services.feature_flags.observability import FeatureFlagMetrics, TimingContext
    ROLLOUT_AVAILABLE = True
except ImportError:
    ROLLOUT_AVAILABLE = False

logger = logging.getLogger(__name__)


class WhatsAppRouter:
    """
    Router para eventos WhatsApp
    
    Responsável por:
    - Resolver thread_key determinística
    - Resolver atribuição SKM
    - Emitir eventos de atribuição
    
    INTEGRAÇÃO COM ROLLOUT:
    - Verifica feature flags via rollout manager
    - Suporta rollout por shopper_id
    """
    
    def __init__(self):
        # Rollout manager (se disponível)
        if ROLLOUT_AVAILABLE:
            self.rollout_manager = get_rollout_manager()
            self.metrics = FeatureFlagMetrics()
        else:
            self.rollout_manager = None
            self.metrics = None
            # Fallback para configuração direta
            self.enabled = getattr(settings, 'WHATSAPP_ROUTING_ENABLED', False)
        
        # Configurações (fallback se rollout não disponível)
        self.group_routing_enabled = getattr(settings, 'WHATSAPP_GROUP_ROUTING_ENABLED', False)
        self.assignment_policy = getattr(settings, 'WHATSAPP_ASSIGNMENT_POLICY', 'default')
    
    def is_enabled_for_shopper(self, shopper_id: Optional[str] = None) -> bool:
        """
        Verifica se roteamento está habilitado para shopper
        
        Args:
            shopper_id: ID do shopper (opcional)
            
        Returns:
            True se habilitado
        """
        if self.rollout_manager:
            return self.rollout_manager.is_enabled(
                'WHATSAPP_ROUTING_ENABLED',
                shopper_id=shopper_id,
                default=False
            )
        return self.enabled
    
    def resolve_thread(self, envelope: EventEnvelope) -> str:
        """
        Resolve thread_key determinística para o evento
        
        Formato:
        - Private: whatsapp:{customer_wa_id}|shopper:{shopper_id}|group:null
        - Group: whatsapp:group:{group_id}|shopper:{shopper_id}
        
        Args:
            envelope: EventEnvelope
        
        Returns:
            thread_key determinística
        """
        # Extrair dados do envelope (suporta dict ou objeto Pydantic)
        if isinstance(envelope, dict):
            routing = envelope.get('routing') or {}
            context = envelope.get('context') or {}
            actor = envelope.get('actor') or {}
        else:
            routing = envelope.routing.dict() if envelope.routing else {}
            context = envelope.context.dict() if envelope.context else {}
            actor = envelope.actor.dict() if envelope.actor else {}
        
        chat_type = context.get('chat_type', 'private')
        wa_id = actor.get('wa_id')
        group_id = None
        if context.get('group'):
            group_id = context['group'].get('id') if isinstance(context['group'], dict) else None
        
        shopper_id = routing.get('shopper_id')
        
        thread_key = generate_thread_key(
            chat_type=chat_type,
            wa_id=wa_id,
            group_id=group_id,
            shopper_id=shopper_id
        )
        
        return thread_key
    
    def resolve_assignment(
        self,
        envelope: EventEnvelope,
        conversation: Optional[WhatsAppConversation] = None
    ) -> Optional[str]:
        """
        Resolve atribuição SKM para o evento
        
        Regras:
        - Se thread já tem skm_id: manter
        - Se mensagem inbound em private: atribuir para SKM padrão do shopper
        - Se mensagem em grupo: identificar entrypoint e atribuir
        - Se forwarded: não reatribuir automaticamente
        
        Args:
            envelope: EventEnvelope
            conversation: WhatsAppConversation (opcional)
        
        Returns:
            skm_id atribuído ou None
        """
        # Extrair shopper_id do envelope
        shopper_id = None
        if isinstance(envelope, dict):
            routing = envelope.get('routing') or {}
            shopper_id = routing.get('shopper_id')
        elif hasattr(envelope, 'routing') and envelope.routing:
            shopper_id = envelope.routing.shopper_id if hasattr(envelope.routing, 'shopper_id') else None
        
        # Verificar se está habilitado para este shopper
        if not self.is_enabled_for_shopper(shopper_id):
            return None
        
        # Logar verificação de flag
        if self.metrics and shopper_id:
            reason = self._get_enable_reason(shopper_id)
            self.metrics.log_flag_check(
                'WHATSAPP_ROUTING_ENABLED',
                True,
                shopper_id=shopper_id,
                reason=reason
            )
        
        return self._do_resolve_assignment(envelope, conversation)
    
    def _get_enable_reason(self, shopper_id: Optional[str]) -> str:
        """
        Obtém razão pela qual flag está habilitada/desabilitada
        
        Args:
            shopper_id: ID do shopper
            
        Returns:
            Razão (allowlist, denylist, percent, global, default)
        """
        if not self.rollout_manager or not shopper_id:
            return 'global'
        
        try:
            config = self.rollout_manager._get_config('WHATSAPP_ROUTING_ENABLED')
            if not config:
                return 'default'
            
            if config.denylist and shopper_id in config.denylist:
                return 'denylist'
            if config.allowlist and shopper_id in config.allowlist:
                return 'allowlist'
            if config.percent_rollout > 0:
                return f'percent_{config.percent_rollout}'
            if config.enabled:
                return 'global'
            return 'default'
        except Exception:
            return 'default'
    
    def _do_resolve_assignment(
        self,
        envelope: EventEnvelope,
        conversation: Optional[WhatsAppConversation] = None
    ) -> Optional[str]:
        """
        Implementação real de resolve_assignment (extraído para reutilização)
        """
        # Extrair dados do envelope (suporta dict ou objeto Pydantic)
        if isinstance(envelope, dict):
            routing = envelope.get('routing') or {}
            context = envelope.get('context') or {}
        else:
            routing = envelope.routing.dict() if envelope.routing else {}
            context = envelope.context.dict() if envelope.context else {}
        
        # Se já tem skm_id no routing, usar
        current_skm_id = routing.get('skm_id')
        if current_skm_id:
            return current_skm_id
        
        # Se conversação já tem skm_id, manter
        if conversation and conversation.skm_id:
            return conversation.skm_id
        
        # Verificar se é mensagem encaminhada
        is_forwarded = bool(context.get('forwarded'))
        
        if is_forwarded:
            # Não reatribuir automaticamente se já houver SKM
            if conversation and conversation.skm_id:
                return conversation.skm_id
            # Se não tem SKM, pode atribuir (depende da política)
        
        # Verificar tipo de chat
        chat_type = context.get('chat_type', 'private')
        
        if chat_type == 'private':
            # Atribuir para SKM padrão do shopper
            shopper_id = routing.get('shopper_id')
            if shopper_id:
                # TODO: Implementar lógica de SKM padrão do shopper
                # Por enquanto, retornar None
                return None
        
        elif chat_type == 'group' and self.group_routing_enabled:
            # Identificar entrypoint
            origin = context.get('origin')
            
            if origin in ['entrypoint', 'mention', 'reaction']:
                # Atribuir por política
                from .assignment import get_assignment_policy
                policy = get_assignment_policy(self.assignment_policy)
                return policy.assign_for_group(envelope, conversation)
        
        return None
    
    def route_event(self, envelope: EventEnvelope) -> Dict[str, Any]:
        """
        Roteia evento completo: resolve thread, atribui SKM, persiste
        
        Args:
            envelope: EventEnvelope
        
        Returns:
            Dict com resultado do roteamento
        """
        # Extrair shopper_id
        shopper_id = None
        if isinstance(envelope, dict):
            routing = envelope.get('routing') or {}
            shopper_id = routing.get('shopper_id')
        elif hasattr(envelope, 'routing') and envelope.routing:
            shopper_id = envelope.routing.shopper_id if hasattr(envelope.routing, 'shopper_id') else None
        
        # Verificar se está habilitado para este shopper
        if not self.is_enabled_for_shopper(shopper_id):
            return {
                'success': False,
                'error': 'Routing não habilitado para este shopper'
            }
        
        try:
            # Resolver thread
            thread_key = self.resolve_thread(envelope)
            
            # Obter ou criar conversação
            if isinstance(envelope, dict):
                routing = envelope.get('routing') or {}
            else:
                routing = envelope.routing.dict() if envelope.routing else {}
            
            shopper_id = routing.get('shopper_id')
            skm_id = routing.get('skm_id')
            
            conversation = get_or_create_conversation(
                thread_key=thread_key,
                shopper_id=shopper_id,
                skm_id=skm_id,
            )
            
            # Resolver atribuição
            assigned_skm_id = self.resolve_assignment(envelope, conversation)
            
            if assigned_skm_id and assigned_skm_id != conversation.skm_id:
                # Atualizar atribuição
                conversation.skm_id = assigned_skm_id
                conversation.save()
                
                # Logar atribuição
                if self.metrics:
                    self.metrics.log_routing_assignment(
                        shopper_id or 'unknown',
                        assigned_skm_id,
                        thread_key,
                        success=True
                    )
                
                # Emitir evento de atribuição
                # TODO: Emitir whatsapp.thread.assigned
                logger.info(f"SKM atribuído: {assigned_skm_id} para thread {thread_key}")
            
            # Persistir evento
            if hasattr(envelope, 'to_dict'):
                event_dict = envelope.to_dict()
            elif isinstance(envelope, dict):
                event_dict = envelope
            else:
                event_dict = envelope.dict() if hasattr(envelope, 'dict') else {}
            
            event_log = append_event(event_dict)
            
            return {
                'success': True,
                'thread_key': thread_key,
                'conversation_id': conversation.conversation_id,
                'skm_id': conversation.skm_id,
                'event_log_id': str(event_log.id),
            }
        
        except Exception as e:
            logger.error(f"Erro ao rotear evento: {e}", exc_info=True)
            
            # Logar erro
            if self.metrics:
                self.metrics.log_routing_assignment(
                    shopper_id or 'unknown',
                    None,
                    thread_key if 'thread_key' in locals() else 'unknown',
                    success=False,
                    error=str(e)
                )
            
            return {
                'success': False,
                'error': str(e)
            }


# Singleton
_router_instance: Optional[WhatsAppRouter] = None


def get_whatsapp_router() -> WhatsAppRouter:
    """Obtém instância singleton do router"""
    global _router_instance
    if _router_instance is None:
        _router_instance = WhatsAppRouter()
    return _router_instance
