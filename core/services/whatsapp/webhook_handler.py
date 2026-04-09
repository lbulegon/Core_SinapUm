"""
Webhook Handler - WhatsApp Gateway Service
===========================================

Handler para receber eventos do WhatsApp Gateway Service (Node.js + Baileys).
Encaminha mensagens para o Evora/VitrineZap para gerenciamento de conversas.
"""
import logging
import threading
from typing import Dict, Any, Optional
import requests as http_requests
from django.http import JsonResponse, HttpRequest
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt

logger = logging.getLogger(__name__)


def _forward_to_evora(payload: Dict[str, Any]) -> Optional[Dict]:
    """Encaminha payload de mensagem para o Evora/VitrineZap em background"""
    evora_url = getattr(settings, 'EVORA_WHATSAPP_WEBHOOK_URL', '')
    if not evora_url:
        return None

    def _do_forward():
        try:
            resp = http_requests.post(
                evora_url,
                json=payload,
                headers={'Content-Type': 'application/json'},
                timeout=15,
            )
            logger.info(
                f"[Evora Forward] status={resp.status_code} url={evora_url}",
                extra={'response_status': resp.status_code}
            )
        except Exception as e:
            logger.error(f"[Evora Forward] Erro ao encaminhar para {evora_url}: {e}")

    thread = threading.Thread(target=_do_forward, daemon=True)
    thread.start()


@csrf_exempt
def handle_incoming_whatsapp_event(request: HttpRequest):
    """
    Processa evento recebido do WhatsApp Gateway Service
    
    Args:
        request: Request HTTP com payload do webhook
    
    Returns:
        Dicionário com resultado do processamento
    """
    try:
        # Valida API Key
        api_key = request.headers.get('X-API-Key', '')
        expected_key = getattr(settings, 'SINAPUM_WHATSAPP_GATEWAY_API_KEY', None)
        
        if expected_key and api_key != expected_key:
            logger.warning(f"API Key inválida no webhook: {api_key[:10]}...")
            return JsonResponse({
                'success': False,
                'error': 'API Key inválida'
            }, status=403)
        
        # Parse payload
        import json
        payload = json.loads(request.body) if request.body else {}
        
        event_type = payload.get('event_type')
        event_payload = payload.get('payload', {})
        timestamp = payload.get('ts')
        
        logger.info(
            f"[WhatsApp Gateway Webhook] Evento recebido: {event_type}",
            extra={
                'event_type': event_type,
                'timestamp': timestamp,
                'payload_keys': list(event_payload.keys()) if isinstance(event_payload, dict) else []
            }
        )
        
        # Processa evento baseado no tipo
        if event_type == 'message':
            return _handle_message_event(event_payload, timestamp)
        elif event_type == 'qr':
            return _handle_qr_event(event_payload, timestamp)
        elif event_type == 'connected':
            return _handle_connected_event(event_payload, timestamp)
        elif event_type == 'disconnected':
            return _handle_disconnected_event(event_payload, timestamp)
        else:
            logger.warning(f"Tipo de evento desconhecido: {event_type}")
            return JsonResponse({
                'success': True,
                'message': f'Evento {event_type} recebido mas não processado'
            })
            
    except Exception as e:
        logger.error(f"Erro ao processar webhook do WhatsApp Gateway: {e}", exc_info=True)
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


def _handle_message_event(payload: Dict[str, Any], timestamp: str) -> Dict[str, Any]:
    """Processa evento de mensagem recebida e encaminha ao Evora"""
    try:
        message_id = payload.get('id')
        from_jid = payload.get('from')
        text = payload.get('text', '')
        number = payload.get('number')
        raw_message = payload.get('raw', {})
        
        logger.info(
            f"[WhatsApp Gateway] Mensagem recebida de {number}",
            extra={
                'message_id': message_id,
                'from': from_jid,
                'number': number,
                'text_length': len(text),
                'text_preview': text[:100] if text else '',
            }
        )
        
        evora_payload = {
            'from': number or (from_jid.split('@')[0] if from_jid else ''),
            'message': text,
            'message_id': message_id,
            'timestamp': timestamp,
            'type': 'text',
            'from_jid': from_jid,
            'raw_payload': raw_message,
            'source': 'baileys_gateway',
        }
        _forward_to_evora(evora_payload)
        
        return JsonResponse({
            'success': True,
            'message': 'Mensagem processada e encaminhada',
            'message_id': message_id
        })
        
    except Exception as e:
        logger.error(f"Erro ao processar evento de mensagem: {e}", exc_info=True)
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


def _handle_qr_event(payload: Dict[str, Any], timestamp: str) -> Dict[str, Any]:
    """Processa evento de QR code gerado"""
    try:
        qr = payload.get('qr')
        
        logger.info(
            "[WhatsApp Gateway] QR Code gerado",
            extra={
                'qr_available': qr is not None,
                'qr_length': len(qr) if qr else 0
            }
        )
        
        # TODO: Armazenar QR code para exibição na UI
        # Exemplo:
        # - Salvar em cache/banco de dados
        # - Notificar frontend via WebSocket
        
        return JsonResponse({
            'success': True,
            'message': 'QR Code recebido'
        })
        
    except Exception as e:
        logger.error(f"Erro ao processar evento de QR: {e}", exc_info=True)
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


def _handle_connected_event(payload: Dict[str, Any], timestamp: str) -> Dict[str, Any]:
    """Processa evento de conexão estabelecida"""
    try:
        logger.info("[WhatsApp Gateway] Conectado ao WhatsApp")
        
        # TODO: Atualizar status no banco de dados
        # Exemplo:
        # - Marcar instância como conectada
        # - Notificar sistema
        
        return JsonResponse({
            'success': True,
            'message': 'Conexão estabelecida'
        })
        
    except Exception as e:
        logger.error(f"Erro ao processar evento de conexão: {e}", exc_info=True)
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


def _handle_disconnected_event(payload: Dict[str, Any], timestamp: str) -> Dict[str, Any]:
    """Processa evento de desconexão"""
    try:
        should_reconnect = payload.get('shouldReconnect', False)
        
        logger.warning(
            "[WhatsApp Gateway] Desconectado do WhatsApp",
            extra={
                'should_reconnect': should_reconnect
            }
        )
        
        # TODO: Atualizar status no banco de dados
        # Exemplo:
        # - Marcar instância como desconectada
        # - Notificar sistema
        
        return JsonResponse({
            'success': True,
            'message': 'Desconexão processada',
            'should_reconnect': should_reconnect
        })
        
    except Exception as e:
        logger.error(f"Erro ao processar evento de desconexão: {e}", exc_info=True)
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)
