# ============================================================================
# ARQUITETURA NOVA - app_whatsapp_gateway.views
# ============================================================================
# Views para gateway WhatsApp multi-tenant
# 
# ANTIGO: app_whatsapp_integration.views (Évora) - instância única
# NOVO: app_whatsapp_gateway.views (Core) - multi-tenant
# ============================================================================

import json
import logging
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.utils import timezone
from django.db import transaction

from .models import EvolutionInstance, WebhookEvent
from .parsers import EvolutionParser
from .services import InstanceService
from .clients import EvolutionClient

logger = logging.getLogger(__name__)

# Inicializar services
instance_service = InstanceService()
evolution_client = EvolutionClient()
evolution_parser = EvolutionParser()


@csrf_exempt
@require_http_methods(["POST"])
def webhook_receiver(request, instance_id: str):
    """
    Recebe webhooks da Evolution API
    
    Endpoint: POST /webhooks/evolution/<instance_id>/messages
    
    DIFERENÇA DO ANTIGO:
    - Antigo: /api/whatsapp/webhook/evolution/ (instância única)
    - Novo: /webhooks/evolution/<instance_id>/messages (multi-tenant)
    """
    try:
        # Ler payload
        payload = json.loads(request.body)
        
        # Log do evento
        with transaction.atomic():
            try:
                instance = EvolutionInstance.objects.get(instance_id=instance_id)
            except EvolutionInstance.DoesNotExist:
                logger.warning(f"Instância {instance_id} não encontrada no webhook")
                return JsonResponse({'status': 'ok', 'message': 'Instância não encontrada'}, status=200)
            
            # Salvar evento no log
            webhook_event = WebhookEvent.objects.create(
                instance=instance,
                event_type=payload.get('event', 'unknown'),
                raw_payload=payload,
                processed=False
            )
        
        # Processar evento de QR Code
        if payload.get('event') in ['qrcode.updated', 'QRCODE_UPDATED']:
            qr_data = evolution_parser.parse_qrcode_event(payload, instance_id)
            if qr_data:
                instance.qrcode = qr_data.get('qrcode')
                instance.qrcode_url = qr_data.get('qrcode_url')
                instance.save()
                webhook_event.processed = True
                webhook_event.save()
                return JsonResponse({'status': 'ok'})
        
        # Processar evento de mensagem
        canonical_event = evolution_parser.parse_webhook(payload, instance_id)
        
        if canonical_event:
            # Preencher shopper_id do instance
            canonical_event['shopper_id'] = instance.shopper_id
            canonical_event['tenant_id'] = instance.shopper_id  # Por enquanto, tenant = shopper
            
            # Marcar evento como processado
            webhook_event.processed = True
            webhook_event.save()
            
            # Integrar com app_conversations
            from app_conversations.services import ConversationService, MessageService
            from app_conversations.models import Conversation, Message
            
            try:
                # Criar ou obter conversa
                conversation, created = ConversationService.get_or_create_by_inbound_event(canonical_event)
                
                # Armazenar mensagem
                message = MessageService.store_inbound(canonical_event, conversation)
                
                logger.info(f"Conversa criada/atualizada: {conversation.id}, Mensagem: {message.id}")
                
                # Se OpenMind estiver habilitado, processar com IA
                from django.conf import settings
                if getattr(settings, 'FEATURE_OPENMIND_ENABLED', False):
                    # Enviar para AI Bridge
                    from app_ai_bridge.services import OpenMindService
                    openmind_service = OpenMindService()
                    ai_response = openmind_service.process_inbound(canonical_event, conversation)
                    
                    if ai_response:
                        # Criar sugestão
                        from app_conversations.services import SuggestionService
                        suggestion = SuggestionService.create_from_ai(conversation, ai_response)
                        logger.info(f"Sugestão criada: {suggestion.id}")
                
            except Exception as e:
                logger.error(f"Erro ao processar evento canônico: {e}", exc_info=True)
                webhook_event.error_message = str(e)
                webhook_event.save()
        
        return JsonResponse({'status': 'ok'})
        
    except json.JSONDecodeError:
        return JsonResponse({'error': 'JSON inválido'}, status=400)
    except Exception as e:
        logger.error(f"Erro ao processar webhook: {e}", exc_info=True)
        return JsonResponse({'error': str(e)}, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def create_instance(request):
    """
    Cria nova instância Evolution para um shopper
    
    Endpoint: POST /instances/evolution/create
    
    Body:
    {
        "shopper_id": "uuid-do-shopper",
        "instance_id": "shopper_123" (opcional)
    }
    """
    try:
        data = json.loads(request.body)
        shopper_id = data.get('shopper_id')
        instance_id = data.get('instance_id')
        
        if not shopper_id:
            return JsonResponse({'error': 'shopper_id é obrigatório'}, status=400)
        
        result = instance_service.create_instance(shopper_id, instance_id)
        
        if result.get('success'):
            return JsonResponse({
                'success': True,
                'instance_id': result['instance'].instance_id,
                'qrcode': result.get('qrcode'),
                'qrcode_url': result.get('qrcode_url'),
            })
        else:
            return JsonResponse({
                'success': False,
                'error': result.get('error')
            }, status=500)
            
    except json.JSONDecodeError:
        return JsonResponse({'error': 'JSON inválido'}, status=400)
    except Exception as e:
        logger.error(f"Erro ao criar instância: {e}", exc_info=True)
        return JsonResponse({'error': str(e)}, status=500)


@require_http_methods(["GET"])
def get_qr(request, instance_id: str):
    """
    Obtém QR Code da instância
    
    Endpoint: GET /instances/evolution/<instance_id>/qr
    
    Query params:
    - shopper_id: (opcional) Para validação
    """
    shopper_id = request.GET.get('shopper_id')
    
    result = instance_service.get_qr(instance_id, shopper_id)
    
    if result.get('success'):
        return JsonResponse({
            'success': True,
            'qrcode': result.get('qrcode'),
            'qrcode_url': result.get('qrcode_url'),
        })
    else:
        return JsonResponse({
            'success': False,
            'error': result.get('error')
        }, status=404)


@csrf_exempt
@require_http_methods(["POST"])
def connect(request, instance_id: str):
    """
    Marca instância como conectada
    
    Endpoint: POST /instances/evolution/<instance_id>/connect
    
    Body:
    {
        "status": "open",
        "phone_number": "+5511999999999",
        "phone_name": "Nome WhatsApp"
    }
    """
    try:
        data = json.loads(request.body)
        status = data.get('status', 'open')
        phone_number = data.get('phone_number')
        phone_name = data.get('phone_name')
        
        success = instance_service.update_status(instance_id, status, phone_number, phone_name)
        
        if success:
            return JsonResponse({'success': True})
        else:
            return JsonResponse({'success': False, 'error': 'Instância não encontrada'}, status=404)
            
    except json.JSONDecodeError:
        return JsonResponse({'error': 'JSON inválido'}, status=400)
    except Exception as e:
        logger.error(f"Erro ao conectar instância: {e}", exc_info=True)
        return JsonResponse({'error': str(e)}, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def send_message(request):
    """
    Envia mensagem via WhatsApp
    
    Endpoint: POST /channels/whatsapp/send
    
    Body:
    {
        "instance_id": "shopper_123",
        "to": "+5511999999999",
        "text": "Mensagem",
        "media_url": "https://..." (opcional)
    }
    """
    try:
        data = json.loads(request.body)
        instance_id = data.get('instance_id')
        to = data.get('to')
        text = data.get('text')
        media_url = data.get('media_url')
        
        if not instance_id or not to:
            return JsonResponse({'error': 'instance_id e to são obrigatórios'}, status=400)
        
        # Validar instância existe
        try:
            instance = EvolutionInstance.objects.get(instance_id=instance_id)
        except EvolutionInstance.DoesNotExist:
            return JsonResponse({'error': 'Instância não encontrada'}, status=404)
        
        # Enviar mensagem
        if media_url:
            result = evolution_client.send_media(instance_id, to, media_url, text or '')
        else:
            if not text:
                return JsonResponse({'error': 'text é obrigatório para mensagens de texto'}, status=400)
            result = evolution_client.send_text(instance_id, to, text)
        
        if result.get('success'):
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

