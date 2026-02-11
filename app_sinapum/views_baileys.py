"""
Views para integração com WhatsApp Gateway Service (Baileys)
"""
from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.conf import settings
from core.services.whatsapp_gateway_client import get_whatsapp_gateway_client
import logging

logger = logging.getLogger(__name__)


@require_http_methods(["GET"])
def whatsapp_gateway_connect(request):
    """
    View principal para conectar WhatsApp via WhatsApp Gateway Service (Baileys)
    Mostra QR code ou status da conexão
    """
    client = get_whatsapp_gateway_client()
    
    # Verificar status inicial
    try:
        status = client.get_status()
        connection_status = status.get('connection', 'disconnected')
        qr_available = status.get('qr_available', False)
    except Exception as e:
        logger.error(f"Erro ao obter status do WhatsApp Gateway: {e}")
        connection_status = 'error'
        qr_available = False
    
    context = {
        'connection_status': connection_status,
        'qr_available': qr_available,
        'gateway_url': getattr(settings, 'SINAPUM_WHATSAPP_GATEWAY_URL', 'http://whatsapp_gateway_service:8007'),
    }
    
    return render(request, 'app_sinapum/whatsapp_gateway_connect.html', context)


@require_http_methods(["POST"])
def whatsapp_gateway_connect_action(request):
    """
    Endpoint AJAX para conectar WhatsApp Gateway
    """
    try:
        client = get_whatsapp_gateway_client()
        result = client.connect()
        
        return JsonResponse({
            'success': result.get('success', False),
            'message': result.get('message', ''),
            'status': result.get('status', 'unknown')
        })
    except Exception as e:
        logger.error(f"Erro ao conectar WhatsApp Gateway: {e}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@require_http_methods(["GET"])
def whatsapp_gateway_get_qr(request):
    """
    Endpoint AJAX para obter QR code
    """
    try:
        client = get_whatsapp_gateway_client()
        
        # Primeiro verificar status
        status = client.get_status()
        connection_status = status.get('connection', 'disconnected')
        
        if connection_status == 'connected':
            return JsonResponse({
                'success': True,
                'connected': True,
                'status': 'connected',
                'message': 'WhatsApp já está conectado'
            })
        
        # Tentar obter QR code
        qr_image = client.get_qr_code()
        
        if qr_image:
            import base64
            qr_base64 = base64.b64encode(qr_image).decode('utf-8')
            return JsonResponse({
                'success': True,
                'qrcode': f'data:image/png;base64,{qr_base64}',
                'status': 'qrcode'
            })
        else:
            return JsonResponse({
                'success': False,
                'error': 'QR code não disponível. Tente conectar primeiro.',
                'status': 'not_available'
            }, status=404)
    except requests.HTTPError as e:
        if e.response.status_code == 404:
            return JsonResponse({
                'success': False,
                'error': 'QR code não disponível. Tente conectar primeiro.',
                'status': 'not_available'
            }, status=404)
        logger.error(f"Erro HTTP ao obter QR code: {e}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=e.response.status_code)
    except Exception as e:
        logger.error(f"Erro ao obter QR code: {e}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@require_http_methods(["GET"])
def whatsapp_gateway_get_status(request):
    """
    Endpoint AJAX para obter status da conexão
    """
    try:
        client = get_whatsapp_gateway_client()
        status = client.get_status()
        
        return JsonResponse({
            'success': True,
            'connection': status.get('connection', 'unknown'),
            'qr_available': status.get('qr_available', False),
            'socket_active': status.get('socket_active', False)
        })
    except Exception as e:
        logger.error(f"Erro ao obter status: {e}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@require_http_methods(["POST"])
def whatsapp_gateway_disconnect(request):
    """
    Endpoint AJAX para desconectar WhatsApp Gateway
    """
    try:
        client = get_whatsapp_gateway_client()
        result = client.disconnect()
        
        return JsonResponse({
            'success': result.get('success', False),
            'message': result.get('message', '')
        })
    except Exception as e:
        logger.error(f"Erro ao desconectar WhatsApp Gateway: {e}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@require_http_methods(["POST"])
def whatsapp_gateway_reset_session(request):
    """
    Endpoint AJAX para resetar sessão WhatsApp Gateway
    """
    try:
        client = get_whatsapp_gateway_client()
        result = client.reset_session()
        
        return JsonResponse({
            'success': result.get('success', False),
            'message': result.get('message', '')
        })
    except Exception as e:
        logger.error(f"Erro ao resetar sessão: {e}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)
