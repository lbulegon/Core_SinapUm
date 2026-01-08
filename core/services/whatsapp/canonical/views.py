"""
Views - WhatsApp Canonical Events v1.0
======================================

Endpoints versionados para receber eventos canônicos.
"""
import logging
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt

from .schemas import EventEnvelope, EventType
from .normalizer import get_event_normalizer
from .publisher import get_event_publisher

logger = logging.getLogger(__name__)


def check_canonical_events_feature_flag(view_func):
    """Decorator para verificar feature flag de eventos canônicos"""
    def wrapper(request, *args, **kwargs):
        if not getattr(settings, 'WHATSAPP_CANONICAL_EVENTS_ENABLED', False):
            return Response(
                {"detail": "Eventos canônicos WhatsApp não habilitados."},
                status=status.HTTP_403_FORBIDDEN
            )
        return view_func(request, *args, **kwargs)
    return wrapper


@api_view(['POST'])
@permission_classes([AllowAny])
@csrf_exempt
@check_canonical_events_feature_flag
def inbound_event(request):
    """
    POST /api/v1/whatsapp/events/inbound
    
    Recebe evento canônico de entrada (mensagem recebida).
    
    Payload esperado (EventEnvelope):
    {
        "event_id": "uuid",
        "event_type": "message.text",
        "event_source": "evolution",
        "instance_key": "instance_123",
        "timestamp": "2024-01-01T12:00:00Z",
        "from_number": "5511999999999",
        "payload": {
            "text": "Mensagem de teste"
        },
        "raw": {...}
    }
    """
    try:
        data = request.data
        
        # Validar e criar EventEnvelope
        envelope = EventEnvelope(**data)
        
        # Verificar se é evento de mensagem
        if not envelope.is_message_event():
            return Response(
                {"detail": "Este endpoint aceita apenas eventos de mensagem."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Publicar evento
        publisher = get_event_publisher()
        event_log = publisher.publish(envelope, emit_signal=True)
        
        if event_log:
            return Response(
                {
                    "success": True,
                    "event_id": envelope.event_id,
                    "event_log_id": str(event_log.id),
                    "message": "Evento processado com sucesso"
                },
                status=status.HTTP_201_CREATED
            )
        else:
            return Response(
                {"success": False, "error": "Erro ao processar evento"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    except Exception as e:
        logger.error(f"Erro ao processar evento inbound: {e}", exc_info=True)
        return Response(
            {"success": False, "error": str(e)},
            status=status.HTTP_400_BAD_REQUEST
        )


@api_view(['POST'])
@permission_classes([AllowAny])
@csrf_exempt
@check_canonical_events_feature_flag
def status_event(request):
    """
    POST /api/v1/whatsapp/events/status
    
    Recebe evento canônico de status (sent, delivered, read, failed).
    
    Payload esperado (EventEnvelope):
    {
        "event_id": "uuid",
        "event_type": "message.delivered",
        "event_source": "evolution",
        "instance_key": "instance_123",
        "timestamp": "2024-01-01T12:00:00Z",
        "message_id": "msg_123",
        "payload": {
            "status": "delivered",
            "message_id": "msg_123"
        },
        "raw": {...}
    }
    """
    try:
        data = request.data
        
        # Validar e criar EventEnvelope
        envelope = EventEnvelope(**data)
        
        # Verificar se é evento de status
        if not envelope.is_status_event():
            return Response(
                {"detail": "Este endpoint aceita apenas eventos de status."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Publicar evento
        publisher = get_event_publisher()
        event_log = publisher.publish(envelope, emit_signal=True)
        
        if event_log:
            return Response(
                {
                    "success": True,
                    "event_id": envelope.event_id,
                    "event_log_id": str(event_log.id),
                    "message": "Status processado com sucesso"
                },
                status=status.HTTP_201_CREATED
            )
        else:
            return Response(
                {"success": False, "error": "Erro ao processar status"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    except Exception as e:
        logger.error(f"Erro ao processar evento de status: {e}", exc_info=True)
        return Response(
            {"success": False, "error": str(e)},
            status=status.HTTP_400_BAD_REQUEST
        )


@api_view(['GET'])
@permission_classes([AllowAny])
def health_check(request):
    """
    GET /api/v1/whatsapp/events/health
    
    Health check para eventos canônicos.
    """
    enabled = getattr(settings, 'WHATSAPP_CANONICAL_EVENTS_ENABLED', False)
    shadow_mode = getattr(settings, 'WHATSAPP_CANONICAL_SHADOW_MODE', False)
    
    return Response({
        "status": "ok",
        "canonical_events_enabled": enabled,
        "shadow_mode": shadow_mode,
        "version": "1.0.0"
    })
