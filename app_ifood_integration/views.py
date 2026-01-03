"""
Views internas para integração iFood (API interna para o serviço ifood_connector)
"""
import json
import logging
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.utils import timezone
from django.core.exceptions import ValidationError
from .models import IfoodStore, IfoodOAuthToken, IfoodSyncRun, MrfooOrder, MrfooPayout

logger = logging.getLogger(__name__)

# Chave de API interna (deve vir de variável de ambiente)
import os
INTERNAL_API_KEY = os.getenv("INTERNAL_API_KEY", "")


def check_internal_api_key(request):
    """Verifica se a requisição possui a chave de API interna válida"""
    if not INTERNAL_API_KEY:
        logger.warning("INTERNAL_API_KEY not configured, allowing all requests")
        return True  # Em desenvolvimento, permite se não configurado
    
    auth_header = request.headers.get('Authorization', '')
    if not auth_header.startswith('Bearer '):
        return False
    
    token = auth_header.replace('Bearer ', '')
    return token == INTERNAL_API_KEY


@csrf_exempt
@require_http_methods(["GET"])
def list_stores(request):
    """
    GET /internal/ifood/stores
    Lista todas as lojas cadastradas.
    """
    if not check_internal_api_key(request):
        return JsonResponse({'error': 'Unauthorized'}, status=401)
    
    stores = IfoodStore.objects.filter(ativo=True).select_related('oauth_token')
    data = []
    for store in stores:
        token = getattr(store, 'oauth_token', None)
        data.append({
            'id': store.id,
            'nome': store.nome,
            'cnpj': store.cnpj,
            'ifood_merchant_id': store.ifood_merchant_id,
            'has_valid_token': store.has_valid_token,
            'token_expires_at': token.expires_at.isoformat() if token else None,
        })
    
    return JsonResponse({'stores': data})


@csrf_exempt
@require_http_methods(["GET"])
def store_status(request, store_id):
    """
    GET /internal/ifood/stores/{id}/status
    Retorna status detalhado de uma loja.
    """
    if not check_internal_api_key(request):
        return JsonResponse({'error': 'Unauthorized'}, status=401)
    
    try:
        store = IfoodStore.objects.get(id=store_id)
    except IfoodStore.DoesNotExist:
        return JsonResponse({'error': 'Store not found'}, status=404)
    
    token = getattr(store, 'oauth_token', None)
    last_sync = IfoodSyncRun.objects.filter(store=store).order_by('-started_at').first()
    
    return JsonResponse({
        'id': store.id,
        'nome': store.nome,
        'ifood_merchant_id': store.ifood_merchant_id,
        'ativo': store.ativo,
        'has_valid_token': store.has_valid_token,
        'token': {
            'expires_at': token.expires_at.isoformat() if token else None,
            'needs_refresh': token.needs_refresh() if token else True,
        } if token else None,
        'last_sync': {
            'kind': last_sync.kind,
            'started_at': last_sync.started_at.isoformat(),
            'ok': last_sync.ok,
            'items_ingested': last_sync.items_ingested,
        } if last_sync else None,
    })


@csrf_exempt
@require_http_methods(["POST"])
def save_oauth_tokens(request, store_id):
    """
    POST /internal/ifood/stores/{id}/tokens
    Salva/atualiza tokens OAuth de uma loja.
    Body: {
        "access_token": "...",
        "refresh_token": "...",
        "expires_in": 3600,
        "token_type": "Bearer",
        "scope": "..."
    }
    """
    if not check_internal_api_key(request):
        return JsonResponse({'error': 'Unauthorized'}, status=401)
    
    try:
        store = IfoodStore.objects.get(id=store_id)
    except IfoodStore.DoesNotExist:
        return JsonResponse({'error': 'Store not found'}, status=404)
    
    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)
    
    # Calcular expires_at
    expires_in = data.get('expires_in', 3600)
    expires_at = timezone.now() + timezone.timedelta(seconds=expires_in)
    
    # Criar ou atualizar token
    token, created = IfoodOAuthToken.objects.update_or_create(
        store=store,
        defaults={
            'access_token': data.get('access_token'),
            'refresh_token': data.get('refresh_token'),
            'token_type': data.get('token_type', 'Bearer'),
            'expires_at': expires_at,
            'scope': data.get('scope', ''),
        }
    )
    
    return JsonResponse({
        'success': True,
        'created': created,
        'expires_at': token.expires_at.isoformat(),
    })


@csrf_exempt
@require_http_methods(["POST"])
def sync_orders(request, store_id):
    """
    POST /internal/ifood/stores/{id}/sync/orders
    Dispara sincronização de pedidos (chamado pelo serviço ifood_connector).
    Body: {
        "date_from": "2024-01-01",
        "date_to": "2024-01-31"
    }
    """
    if not check_internal_api_key(request):
        return JsonResponse({'error': 'Unauthorized'}, status=401)
    
    try:
        store = IfoodStore.objects.get(id=store_id)
    except IfoodStore.DoesNotExist:
        return JsonResponse({'error': 'Store not found'}, status=404)
    
    # Esta view apenas registra a solicitação
    # A sincronização real é feita pelo serviço ifood_connector
    return JsonResponse({
        'message': 'Sync request registered. Use ifood_connector service to execute sync.',
        'store_id': store_id,
    })


@csrf_exempt
@require_http_methods(["POST"])
def sync_finance(request, store_id):
    """
    POST /internal/ifood/stores/{id}/sync/finance
    Dispara sincronização financeira (chamado pelo serviço ifood_connector).
    Body: {
        "period": "2024-01"
    }
    """
    if not check_internal_api_key(request):
        return JsonResponse({'error': 'Unauthorized'}, status=401)
    
    try:
        store = IfoodStore.objects.get(id=store_id)
    except IfoodStore.DoesNotExist:
        return JsonResponse({'error': 'Store not found'}, status=404)
    
    return JsonResponse({
        'message': 'Sync request registered. Use ifood_connector service to execute sync.',
        'store_id': store_id,
    })


@csrf_exempt
@require_http_methods(["POST"])
def create_sync_run(request, store_id):
    """
    POST /internal/ifood/stores/{id}/sync-runs
    Cria um registro de execução de sincronização.
    Body: {
        "kind": "orders",
        "started_at": "2024-01-01T10:00:00Z"
    }
    """
    if not check_internal_api_key(request):
        return JsonResponse({'error': 'Unauthorized'}, status=401)
    
    try:
        store = IfoodStore.objects.get(id=store_id)
    except IfoodStore.DoesNotExist:
        return JsonResponse({'error': 'Store not found'}, status=404)
    
    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)
    
    sync_run = IfoodSyncRun.objects.create(
        store=store,
        kind=data.get('kind', 'orders'),
        started_at=timezone.now(),
    )
    
    return JsonResponse({
        'sync_run_id': sync_run.id,
        'started_at': sync_run.started_at.isoformat(),
    })


@csrf_exempt
@require_http_methods(["PATCH"])
def update_sync_run(request, sync_run_id):
    """
    PATCH /internal/ifood/sync-runs/{id}
    Atualiza um registro de execução de sincronização.
    Body: {
        "finished_at": "2024-01-01T10:05:00Z",
        "ok": true,
        "items_ingested": 150,
        "error": null,
        "metadata": {}
    }
    """
    if not check_internal_api_key(request):
        return JsonResponse({'error': 'Unauthorized'}, status=401)
    
    try:
        sync_run = IfoodSyncRun.objects.get(id=sync_run_id)
    except IfoodSyncRun.DoesNotExist:
        return JsonResponse({'error': 'Sync run not found'}, status=404)
    
    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)
    
    if 'finished_at' in data:
        sync_run.finished_at = timezone.now()
    if 'ok' in data:
        sync_run.ok = data['ok']
    if 'items_ingested' in data:
        sync_run.items_ingested = data['items_ingested']
    if 'error' in data:
        sync_run.error = data['error']
    if 'metadata' in data:
        sync_run.metadata = data['metadata']
    
    sync_run.save()
    
    return JsonResponse({
        'success': True,
        'sync_run_id': sync_run.id,
    })


@csrf_exempt
@require_http_methods(["POST"])
def save_order(request):
    """
    POST /internal/mrfoo/orders
    Salva um pedido normalizado.
    Body: {
        "store_id": 1,
        "order_id": "IFOOD-123",
        "created_at": "2024-01-01T10:00:00Z",
        "status": "CONFIRMED",
        "total_value": 45.90,
        "channel": "ifood",
        "raw_json": {}
    }
    """
    if not check_internal_api_key(request):
        return JsonResponse({'error': 'Unauthorized'}, status=401)
    
    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)
    
    try:
        store = IfoodStore.objects.get(id=data['store_id'])
    except IfoodStore.DoesNotExist:
        return JsonResponse({'error': 'Store not found'}, status=404)
    
    order, created = MrfooOrder.objects.update_or_create(
        order_id=data['order_id'],
        defaults={
            'store': store,
            'created_at': data.get('created_at'),
            'status': data.get('status', 'PENDING'),
            'total_value': data.get('total_value'),
            'channel': data.get('channel', 'ifood'),
            'raw_json': data.get('raw_json', {}),
        }
    )
    
    return JsonResponse({
        'success': True,
        'created': created,
        'order_id': order.id,
    })


@csrf_exempt
@require_http_methods(["POST"])
def save_payout(request):
    """
    POST /internal/mrfoo/payouts
    Salva um repasse normalizado.
    Body: {
        "store_id": 1,
        "payout_id": "PAYOUT-123",
        "reference_period": "2024-01",
        "gross": 10000.00,
        "fees": 1500.00,
        "net": 8500.00,
        "channel": "ifood",
        "raw_json": {}
    }
    """
    if not check_internal_api_key(request):
        return JsonResponse({'error': 'Unauthorized'}, status=401)
    
    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)
    
    try:
        store = IfoodStore.objects.get(id=data['store_id'])
    except IfoodStore.DoesNotExist:
        return JsonResponse({'error': 'Store not found'}, status=404)
    
    payout, created = MrfooPayout.objects.update_or_create(
        payout_id=data['payout_id'],
        defaults={
            'store': store,
            'reference_period': data.get('reference_period'),
            'gross': data.get('gross'),
            'fees': data.get('fees', 0),
            'net': data.get('net'),
            'channel': data.get('channel', 'ifood'),
            'raw_json': data.get('raw_json', {}),
        }
    )
    
    return JsonResponse({
        'success': True,
        'created': created,
        'payout_id': payout.id,
    })


@csrf_exempt
@require_http_methods(["GET"])
def list_orders(request):
    """
    GET /internal/mrfoo/orders?store_id=&date_from=&date_to=
    Lista pedidos normalizados (para consumo do MrFoo).
    """
    if not check_internal_api_key(request):
        return JsonResponse({'error': 'Unauthorized'}, status=401)
    
    store_id = request.GET.get('store_id')
    date_from = request.GET.get('date_from')
    date_to = request.GET.get('date_to')
    
    queryset = MrfooOrder.objects.all()
    
    if store_id:
        queryset = queryset.filter(store_id=store_id)
    if date_from:
        queryset = queryset.filter(created_at__gte=date_from)
    if date_to:
        queryset = queryset.filter(created_at__lte=date_to)
    
    orders = queryset.select_related('store').order_by('-created_at')[:1000]
    
    data = []
    for order in orders:
        data.append({
            'id': order.id,
            'order_id': order.order_id,
            'store': {
                'id': order.store.id,
                'nome': order.store.nome,
            },
            'created_at': order.created_at.isoformat(),
            'status': order.status,
            'total_value': str(order.total_value),
            'channel': order.channel,
        })
    
    return JsonResponse({'orders': data, 'count': len(data)})


@csrf_exempt
@require_http_methods(["GET"])
def list_payouts(request):
    """
    GET /internal/mrfoo/payouts?store_id=&period=
    Lista repasses normalizados (para consumo do MrFoo).
    """
    if not check_internal_api_key(request):
        return JsonResponse({'error': 'Unauthorized'}, status=401)
    
    store_id = request.GET.get('store_id')
    period = request.GET.get('period')
    
    queryset = MrfooPayout.objects.all()
    
    if store_id:
        queryset = queryset.filter(store_id=store_id)
    if period:
        queryset = queryset.filter(reference_period=period)
    
    payouts = queryset.select_related('store').order_by('-reference_period', '-synced_at')
    
    data = []
    for payout in payouts:
        data.append({
            'id': payout.id,
            'payout_id': payout.payout_id,
            'store': {
                'id': payout.store.id,
                'nome': payout.store.nome,
            },
            'reference_period': payout.reference_period,
            'gross': str(payout.gross),
            'fees': str(payout.fees),
            'net': str(payout.net),
            'channel': payout.channel,
        })
    
    return JsonResponse({'payouts': data, 'count': len(data)})

