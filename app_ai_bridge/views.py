# ============================================================================
# ARQUITETURA NOVA - app_ai_bridge.views
# ============================================================================
# Views para ponte com OpenMind
# ============================================================================

import json
import logging
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

logger = logging.getLogger(__name__)


@csrf_exempt
@require_http_methods(["POST"])
def inbound(request):
    """
    Recebe evento canônico e envia para OpenMind
    
    Endpoint: POST /ai/inbound
    
    Body:
    {
        "event": {...},  # Evento Canônico
        "context": {
            "last_messages": [...],
            "cart": {...},
            "customer": {...}
        }
    }
    """
    try:
        data = json.loads(request.body)
        event = data.get('event')
        context = data.get('context', {})
        
        if not event:
            return JsonResponse({'error': 'event é obrigatório'}, status=400)
        
        # Buscar conversa
        from app_conversations.models import Conversation
        conversation_id = event.get('conversation_id')
        if not conversation_id:
            return JsonResponse({'error': 'conversation_id é obrigatório no evento'}, status=400)
        
        try:
            conversation = Conversation.objects.get(id=conversation_id)
        except Conversation.DoesNotExist:
            return JsonResponse({'error': 'Conversa não encontrada'}, status=404)
        
        # Processar com OpenMind
        from .services import OpenMindService
        openmind_service = OpenMindService()
        ai_response = openmind_service.process_inbound(event, conversation)
        
        if ai_response:
            # Criar sugestão
            from app_conversations.services import SuggestionService
            suggestion = SuggestionService.create_from_ai(conversation, ai_response)
            
            return JsonResponse({
                'success': True,
                'suggestion_id': str(suggestion.id),
                'intent': ai_response.get('intent'),
                'confidence': ai_response.get('confidence'),
                'suggested_reply': ai_response.get('suggested_reply'),
                'actions': ai_response.get('actions', []),
            })
        else:
            return JsonResponse({
                'success': False,
                'error': 'Erro ao processar com OpenMind'
            }, status=500)
        
    except json.JSONDecodeError:
        return JsonResponse({'error': 'JSON inválido'}, status=400)
    except Exception as e:
        logger.error(f"Erro ao processar inbound: {e}", exc_info=True)
        return JsonResponse({'error': str(e)}, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def outbound(request):
    """
    Recebe resposta do OpenMind e cria sugestão
    
    Endpoint: POST /ai/outbound
    
    Body:
    {
        "conversation_id": "uuid",
        "intent": "buscar_produto",
        "confidence": 0.9,
        "suggested_reply": "Encontrei estes produtos...",
        "actions": [...],
        "mode_recommendation": "assistido",
        "handoff_recommendation": false
    }
    """
    try:
        data = json.loads(request.body)
        conversation_id = data.get('conversation_id')
        
        if not conversation_id:
            return JsonResponse({'error': 'conversation_id é obrigatório'}, status=400)
        
        # Buscar conversa
        from app_conversations.models import Conversation
        try:
            conversation = Conversation.objects.get(id=conversation_id)
        except Conversation.DoesNotExist:
            return JsonResponse({'error': 'Conversa não encontrada'}, status=404)
        
        # Criar sugestão
        from app_conversations.services import SuggestionService
        suggestion = SuggestionService.create_from_ai(conversation, data)
        
        # Atualizar modo se recomendado
        mode_recommendation = data.get('mode_recommendation')
        if mode_recommendation in ['assistido', 'auto']:
            conversation.mode = mode_recommendation
            conversation.save()
        
        return JsonResponse({
            'success': True,
            'suggestion_id': str(suggestion.id),
        })
        
    except json.JSONDecodeError:
        return JsonResponse({'error': 'JSON inválido'}, status=400)
    except Exception as e:
        logger.error(f"Erro ao processar outbound: {e}", exc_info=True)
        return JsonResponse({'error': str(e)}, status=500)

