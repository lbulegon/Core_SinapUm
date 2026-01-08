# ============================================================================
# ARQUITETURA NOVA - app_conversations.views
# ============================================================================
# Views para Console API - Conversas e Sugestões
# ============================================================================

import json
import logging
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.core.paginator import Paginator
from django.db.models import Q

from .models import Conversation, Message, Suggestion
from .services import ConversationService, MessageService, SuggestionService
from app_whatsapp_gateway.clients import EvolutionClient

logger = logging.getLogger(__name__)

# Inicializar services
evolution_client = EvolutionClient()


@require_http_methods(["GET"])
def list_conversations(request):
    """
    Lista conversas de um shopper
    
    Endpoint: GET /console/conversations?shopper_id=...
    
    Query params:
    - shopper_id: ID do Shopper (obrigatório)
    - page: Número da página (opcional)
    - limit: Itens por página (opcional, default: 20)
    """
    shopper_id = request.GET.get('shopper_id')
    
    if not shopper_id:
        return JsonResponse({'error': 'shopper_id é obrigatório'}, status=400)
    
    # Validar que o shopper_id é do usuário autenticado (TODO: implementar auth)
    
    # Buscar conversas
    conversations = Conversation.objects.filter(
        shopper_id=shopper_id
    ).order_by('-last_message_at', '-created_at')
    
    # Paginação
    page = int(request.GET.get('page', 1))
    limit = int(request.GET.get('limit', 20))
    paginator = Paginator(conversations, limit)
    page_obj = paginator.get_page(page)
    
    # Serializar
    data = {
        'count': paginator.count,
        'page': page,
        'pages': paginator.num_pages,
        'results': [
            {
                'id': str(conv.id),
                'conversation_key': conv.conversation_key,
                'customer_phone': conv.customer_phone,
                'customer_name': conv.customer_name,
                'chat_type': conv.chat_type,
                'mode': conv.mode,
                'owner': conv.owner,
                'tags': conv.tags,
                'last_message_at': conv.last_message_at.isoformat() if conv.last_message_at else None,
                'created_at': conv.created_at.isoformat(),
            }
            for conv in page_obj
        ]
    }
    
    return JsonResponse(data)


@require_http_methods(["GET"])
def get_conversation(request, conversation_id: str):
    """
    Obtém detalhes de uma conversa
    
    Endpoint: GET /console/conversations/<conversation_id>
    
    Query params:
    - shopper_id: ID do Shopper (obrigatório, para validação)
    """
    shopper_id = request.GET.get('shopper_id')
    
    if not shopper_id:
        return JsonResponse({'error': 'shopper_id é obrigatório'}, status=400)
    
    try:
        conversation = Conversation.objects.get(id=conversation_id, shopper_id=shopper_id)
    except Conversation.DoesNotExist:
        return JsonResponse({'error': 'Conversa não encontrada'}, status=404)
    
    # Buscar últimas mensagens
    messages = Message.objects.filter(
        conversation=conversation
    ).order_by('timestamp', 'created_at')[:50]  # Últimas 50 mensagens
    
    # Serializar
    data = {
        'id': str(conversation.id),
        'conversation_key': conversation.conversation_key,
        'customer_phone': conversation.customer_phone,
        'customer_name': conversation.customer_name,
        'chat_type': conversation.chat_type,
        'mode': conversation.mode,
        'owner': conversation.owner,
        'tags': conversation.tags,
        'last_message_at': conversation.last_message_at.isoformat() if conversation.last_message_at else None,
        'created_at': conversation.created_at.isoformat(),
        'messages': [
            {
                'id': str(msg.id),
                'direction': msg.direction,
                'message_type': msg.message_type,
                'text': msg.text,
                'media_url': msg.media_url,
                'sent_by': msg.sent_by,
                'timestamp': msg.timestamp.isoformat(),
            }
            for msg in messages
        ]
    }
    
    return JsonResponse(data)


@require_http_methods(["GET"])
def get_suggestions(request, conversation_id: str):
    """
    Obtém sugestões pendentes de uma conversa
    
    Endpoint: GET /console/conversations/<conversation_id>/suggestions
    
    Query params:
    - shopper_id: ID do Shopper (obrigatório)
    - status: Filtrar por status (opcional: pending, sent, dismissed)
    """
    shopper_id = request.GET.get('shopper_id')
    status_filter = request.GET.get('status', 'pending')
    
    if not shopper_id:
        return JsonResponse({'error': 'shopper_id é obrigatório'}, status=400)
    
    try:
        conversation = Conversation.objects.get(id=conversation_id, shopper_id=shopper_id)
    except Conversation.DoesNotExist:
        return JsonResponse({'error': 'Conversa não encontrada'}, status=404)
    
    # Buscar sugestões
    suggestions = Suggestion.objects.filter(
        conversation=conversation,
        status=status_filter
    ).order_by('-created_at')
    
    # Serializar
    data = {
        'conversation_id': str(conversation.id),
        'suggestions': [
            {
                'id': str(sug.id),
                'intent': sug.intent,
                'confidence': sug.confidence,
                'suggested_reply': sug.suggested_reply,
                'actions': sug.actions,
                'status': sug.status,
                'created_at': sug.created_at.isoformat(),
            }
            for sug in suggestions
        ]
    }
    
    return JsonResponse(data)


@csrf_exempt
@require_http_methods(["POST"])
def send_suggestion(request, suggestion_id: str):
    """
    Envia uma sugestão (marca como enviada e envia mensagem)
    
    Endpoint: POST /console/suggestions/<suggestion_id>/send
    
    Body:
    {
        "shopper_id": "uuid-do-shopper"
    }
    """
    try:
        data = json.loads(request.body)
        shopper_id = data.get('shopper_id')
        
        if not shopper_id:
            return JsonResponse({'error': 'shopper_id é obrigatório'}, status=400)
        
        try:
            suggestion = Suggestion.objects.get(id=suggestion_id)
            conversation = suggestion.conversation
            
            # Validar shopper_id
            if conversation.shopper_id != shopper_id:
                return JsonResponse({'error': 'Sugestão não pertence a este shopper'}, status=403)
            
            # Obter instância
            from app_whatsapp_gateway.models import EvolutionInstance
            try:
                instance = EvolutionInstance.objects.get(
                    instance_id=conversation.instance_id,
                    shopper_id=shopper_id
                )
            except EvolutionInstance.DoesNotExist:
                return JsonResponse({'error': 'Instância não encontrada'}, status=404)
            
            # Enviar mensagem via Evolution
            result = evolution_client.send_text(
                instance.instance_id,
                conversation.customer_phone,
                suggestion.suggested_reply
            )
            
            if result.get('success'):
                # Marcar sugestão como enviada
                SuggestionService.mark_sent(suggestion_id)
                
                # Criar mensagem de saída
                MessageService.store_outbound(
                    conversation,
                    suggestion.suggested_reply,
                    sent_by=Message.SentBy.SHOPPER
                )
                
                return JsonResponse({
                    'success': True,
                    'message_id': result.get('message_id'),
                })
            else:
                return JsonResponse({
                    'success': False,
                    'error': result.get('error', 'Erro ao enviar mensagem')
                }, status=500)
                
        except Suggestion.DoesNotExist:
            return JsonResponse({'error': 'Sugestão não encontrada'}, status=404)
            
    except json.JSONDecodeError:
        return JsonResponse({'error': 'JSON inválido'}, status=400)
    except Exception as e:
        logger.error(f"Erro ao enviar sugestão: {e}", exc_info=True)
        return JsonResponse({'error': str(e)}, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def send_message(request):
    """
    Envia mensagem manual do shopper
    
    Endpoint: POST /console/messages/send
    
    Body:
    {
        "shopper_id": "uuid-do-shopper",
        "conversation_id": "uuid-da-conversa",
        "text": "Mensagem",
        "media_url": "https://..." (opcional)
    }
    """
    try:
        data = json.loads(request.body)
        shopper_id = data.get('shopper_id')
        conversation_id = data.get('conversation_id')
        text = data.get('text')
        media_url = data.get('media_url')
        
        if not all([shopper_id, conversation_id, text]):
            return JsonResponse({'error': 'shopper_id, conversation_id e text são obrigatórios'}, status=400)
        
        try:
            conversation = Conversation.objects.get(id=conversation_id, shopper_id=shopper_id)
        except Conversation.DoesNotExist:
            return JsonResponse({'error': 'Conversa não encontrada'}, status=404)
        
        # Obter instância
        from app_whatsapp_gateway.models import EvolutionInstance
        try:
            instance = EvolutionInstance.objects.get(
                instance_id=conversation.instance_id,
                shopper_id=shopper_id
            )
        except EvolutionInstance.DoesNotExist:
            return JsonResponse({'error': 'Instância não encontrada'}, status=404)
        
        # Enviar mensagem
        if media_url:
            result = evolution_client.send_media(instance.instance_id, conversation.customer_phone, media_url, text)
        else:
            result = evolution_client.send_text(instance.instance_id, conversation.customer_phone, text)
        
        if result.get('success'):
            # Armazenar mensagem
            MessageService.store_outbound(
                conversation,
                text,
                sent_by=Message.SentBy.SHOPPER,
                media_url=media_url
            )
            
            return JsonResponse({
                'success': True,
                'message_id': result.get('message_id'),
            })
        else:
            return JsonResponse({
                'success': False,
                'error': result.get('error', 'Erro ao enviar mensagem')
            }, status=500)
            
    except json.JSONDecodeError:
        return JsonResponse({'error': 'JSON inválido'}, status=400)
    except Exception as e:
        logger.error(f"Erro ao enviar mensagem: {e}", exc_info=True)
        return JsonResponse({'error': str(e)}, status=500)

