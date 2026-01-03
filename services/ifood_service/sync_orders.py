"""
Módulo de sincronização de pedidos do iFood
"""
import logging
import requests
from datetime import datetime
from typing import Dict, Any, Optional
from settings import Settings
from client import IfoodAPIClient
from auth import OAuthHandler

logger = logging.getLogger(__name__)


async def sync_orders_for_store(
    settings: Settings,
    store_id: int,
    date_from: Optional[str] = None,
    date_to: Optional[str] = None
) -> Dict[str, Any]:
    """
    Sincroniza pedidos do iFood para uma loja específica.
    
    Args:
        settings: Configurações do serviço
        store_id: ID da loja no Core
        date_from: Data inicial (YYYY-MM-DD)
        date_to: Data final (YYYY-MM-DD)
    
    Returns:
        Dict com resultado da sincronização
    """
    # 1. Buscar dados da loja no Core
    try:
        store_response = requests.get(
            f"{settings.CORE_INTERNAL_BASE_URL}/internal/ifood/stores/{store_id}/status",
            headers={"Authorization": f"Bearer {settings.INTERNAL_API_KEY}"},
            timeout=10
        )
        store_response.raise_for_status()
        store_data = store_response.json()
    except requests.RequestException as e:
        logger.error(f"Error fetching store: {e}")
        raise Exception(f"Failed to fetch store: {e}")
    
    if not store_data.get('has_valid_token'):
        raise Exception("Store does not have valid OAuth token")
    
    # 2. Criar sync_run no Core
    try:
        sync_run_response = requests.post(
            f"{settings.CORE_INTERNAL_BASE_URL}/internal/ifood/stores/{store_id}/sync-runs",
            headers={
                "Authorization": f"Bearer {settings.INTERNAL_API_KEY}",
                "Content-Type": "application/json"
            },
            json={"kind": "orders"},
            timeout=10
        )
        sync_run_response.raise_for_status()
        sync_run_data = sync_run_response.json()
        sync_run_id = sync_run_data['sync_run_id']
    except requests.RequestException as e:
        logger.error(f"Error creating sync run: {e}")
        raise Exception(f"Failed to create sync run: {e}")
    
    # 3. Buscar access_token (com refresh se necessário)
    # TODO: Implementar busca de token do Core e refresh automático
    # Por enquanto, assumimos que o token está válido
    
    # 4. Buscar pedidos do iFood
    api_client = IfoodAPIClient(settings)
    oauth_handler = OAuthHandler(settings)
    
    # TODO: Buscar token do Core e verificar expiração
    # Por enquanto, placeholder
    access_token = "PLACEHOLDER_TOKEN"  # Substituir por busca real no Core
    merchant_id = store_data['ifood_merchant_id']
    
    try:
        orders_data = api_client.get_orders(
            access_token=access_token,
            merchant_id=merchant_id,
            date_from=date_from,
            date_to=date_to
        )
    except Exception as e:
        # Registrar erro no sync_run
        requests.patch(
            f"{settings.CORE_INTERNAL_BASE_URL}/internal/ifood/sync-runs/{sync_run_id}",
            headers={
                "Authorization": f"Bearer {settings.INTERNAL_API_KEY}",
                "Content-Type": "application/json"
            },
            json={
                "finished_at": datetime.utcnow().isoformat(),
                "ok": False,
                "error": str(e)
            },
            timeout=10
        )
        raise
    
    # 5. Normalizar e salvar pedidos no Core
    items_ingested = 0
    errors = []
    
    orders = orders_data.get('data', []) if isinstance(orders_data, dict) else orders_data
    
    for order_data in orders:
        try:
            # Normalizar pedido
            normalized_order = {
                "store_id": store_id,
                "order_id": order_data.get('id') or order_data.get('orderId'),
                "created_at": order_data.get('createdAt') or order_data.get('created_at'),
                "status": order_data.get('status', 'PENDING'),
                "total_value": order_data.get('totalValue') or order_data.get('total_value', 0),
                "channel": "ifood",
                "raw_json": order_data,
            }
            
            # Salvar no Core
            save_response = requests.post(
                f"{settings.CORE_INTERNAL_BASE_URL}/internal/mrfoo/orders/save",
                headers={
                    "Authorization": f"Bearer {settings.INTERNAL_API_KEY}",
                    "Content-Type": "application/json"
                },
                json=normalized_order,
                timeout=10
            )
            
            if save_response.status_code == 200:
                items_ingested += 1
            else:
                errors.append(f"Failed to save order {normalized_order['order_id']}")
        
        except Exception as e:
            errors.append(f"Error processing order: {e}")
            logger.error(f"Error processing order: {e}")
    
    # 6. Atualizar sync_run
    try:
        requests.patch(
            f"{settings.CORE_INTERNAL_BASE_URL}/internal/ifood/sync-runs/{sync_run_id}",
            headers={
                "Authorization": f"Bearer {settings.INTERNAL_API_KEY}",
                "Content-Type": "application/json"
            },
            json={
                "finished_at": datetime.utcnow().isoformat(),
                "ok": len(errors) == 0,
                "items_ingested": items_ingested,
                "error": "; ".join(errors) if errors else None,
                "metadata": {
                    "date_from": date_from,
                    "date_to": date_to,
                    "total_orders": len(orders),
                }
            },
            timeout=10
        )
    except Exception as e:
        logger.error(f"Error updating sync run: {e}")
    
    return {
        "success": True,
        "sync_run_id": sync_run_id,
        "items_ingested": items_ingested,
        "errors": errors,
    }

