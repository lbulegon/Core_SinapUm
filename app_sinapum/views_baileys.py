"""
Views para integração com WhatsApp Gateway Service (Baileys)
"""
import logging
import os

import requests
from django.conf import settings
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

from core.services.whatsapp_gateway_client import get_whatsapp_gateway_client

logger = logging.getLogger(__name__)

# Endpoints Baileys permitidos no proxy (whitelist)
BAILEYS_PROXY_ALLOWED = {"v1/status", "v1/connect", "v1/qr", "v1/session/reset", "v1/disconnect"}


@csrf_exempt
def whatsapp_baileys_proxy(request, endpoint):
    """
    Proxy transparente para a API do Baileys. Expõe /whatsapp/proxy/v1/* com
    a mesma interface do whatsapp_gateway_service (porta 8007).

    Usado pelo Évora/VitrineZap para acessar o Baileys via porta Django (5000),
    evitando expor a porta 8007 externamente.

    Base URL no Évora: WHATSAPP_BAILEYS_GATEWAY_URL=http://69.169.102.84:5000/whatsapp/proxy
    """
    endpoint = endpoint.rstrip('/')  # normalizar: v1/status/ -> v1/status (APPEND_SLASH)
    if endpoint not in BAILEYS_PROXY_ALLOWED:
        return JsonResponse({"error": "Endpoint não permitido"}, status=404)

    method_valid = (
        (endpoint in ("v1/connect", "v1/session/reset", "v1/disconnect") and request.method == "POST")
        or (endpoint in ("v1/status", "v1/qr") and request.method == "GET")
    )
    if not method_valid:
        return JsonResponse({"error": f"Método {request.method} não permitido para {endpoint}"}, status=405)

    client = get_whatsapp_gateway_client()
    base_url = client.base_url.rstrip("/")
    url = f"{base_url}/{endpoint}"

    api_key = getattr(request, "headers", {}).get("X-API-Key") or request.META.get("HTTP_X_API_KEY") or client.api_key or ""
    headers = {"X-API-Key": api_key}
    if not headers["X-API-Key"]:
        return JsonResponse({"error": "X-API-Key ausente"}, status=401)

    # Sessão por usuário: repassar X-Instance-Id para o gateway (ex: user_123)
    instance_id = getattr(request, "headers", {}).get("X-Instance-Id") or request.META.get("HTTP_X_INSTANCE_ID")
    if instance_id:
        headers["X-Instance-Id"] = instance_id

    timeout = 20 if endpoint == "v1/connect" else 15
    try:
        if request.method == "POST":
            resp = requests.post(url, headers=headers, timeout=timeout)
        else:
            resp = requests.get(url, headers=headers, timeout=timeout)
    except requests.RequestException as e:
        logger.warning(f"[Baileys Proxy] Erro de rede: {e}")
        return JsonResponse(
            {"error": "Service Unavailable", "detail": str(e)},
            status=503,
        )

    if endpoint == "v1/qr":
        if resp.status_code == 200:
            return HttpResponse(resp.content, content_type="image/png")
        if resp.status_code == 404:
            return JsonResponse(resp.json() if resp.text else {"error": "QR não disponível"}, status=404)
        return HttpResponse(resp.content, status=resp.status_code)

    try:
        data = resp.json()
    except Exception:
        data = {"error": resp.text[:500] if resp.text else "Resposta inválida"}
    return JsonResponse(data, status=resp.status_code, safe=False)


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
