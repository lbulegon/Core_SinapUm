# ============================================================================
# ARQUITETURA NOVA - app_ai_bridge.services.openmind_service
# ============================================================================
# Service para comunicação com OpenMind
# ============================================================================

import requests
import logging
from typing import Dict, Any, Optional, List
from django.conf import settings
from app_conversations.models import Conversation, Message

logger = logging.getLogger(__name__)


class OpenMindService:
    """
    Service para comunicação com OpenMind AI
    """
    
    def __init__(self, base_url: Optional[str] = None, token: Optional[str] = None):
        """
        Inicializa cliente OpenMind
        
        Args:
            base_url: URL base do OpenMind (default: OPENMIND_BASE_URL)
            token: Token de autenticação (default: OPENMIND_TOKEN)
        """
        self.base_url = base_url or getattr(settings, 'OPENMIND_BASE_URL', 'http://69.169.102.84:8001')
        self.token = token or getattr(settings, 'OPENMIND_TOKEN', '')
        self.timeout = getattr(settings, 'OPENMIND_TIMEOUT', 30)
        
        # Headers
        self.headers = {
            'Content-Type': 'application/json',
        }
        if self.token:
            self.headers['Authorization'] = f'Bearer {self.token}'
    
    def _request(self, method: str, endpoint: str, data: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Faz requisição HTTP para OpenMind
        
        Args:
            method: Método HTTP
            endpoint: Endpoint da API
            data: Dados para enviar
        
        Returns:
            Resposta da API
        """
        url = f"{self.base_url}{endpoint}"
        
        try:
            response = requests.request(
                method=method,
                url=url,
                headers=self.headers,
                json=data,
                timeout=self.timeout
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Erro ao fazer requisição para OpenMind: {e}")
            return {'success': False, 'error': str(e)}
    
    def process_inbound(self, canonical_event: Dict[str, Any], conversation: Conversation) -> Optional[Dict[str, Any]]:
        """
        Processa evento canônico e retorna sugestão da IA
        
        Args:
            canonical_event: Evento canônico
            conversation: Conversa
        
        Returns:
            Resposta da IA:
            {
                'intent': str,
                'confidence': float,
                'suggested_reply': str,
                'actions': list
            } ou None se erro
        """
        # Buscar últimas mensagens para contexto
        last_messages = Message.objects.filter(
            conversation=conversation
        ).order_by('-timestamp')[:10]  # Últimas 10 mensagens
        
        # Construir contexto
        context = {
            'last_messages': [
                {
                    'direction': msg.direction,
                    'text': msg.text,
                    'timestamp': msg.timestamp.isoformat(),
                }
                for msg in last_messages
            ],
            'conversation': {
                'id': str(conversation.id),
                'customer_phone': conversation.customer_phone,
                'customer_name': conversation.customer_name,
                'mode': conversation.mode,
            }
        }
        
        # Preparar payload
        payload = {
            'event': canonical_event,
            'context': context,
        }
        
        # Chamar OpenMind
        result = self._request('POST', '/api/v1/process-message', payload)
        
        if result.get('success'):
            return {
                'intent': result.get('intent', 'unknown'),
                'confidence': result.get('confidence', 0.0),
                'suggested_reply': result.get('suggested_reply', ''),
                'actions': result.get('actions', []),
            }
        else:
            logger.warning(f"OpenMind retornou erro: {result.get('error')}")
            # Fallback: sugestão padrão
            return {
                'intent': 'unknown',
                'confidence': 0.0,
                'suggested_reply': 'Entendi. Vou te ajudar. O que você procura?',
                'actions': [],
            }

