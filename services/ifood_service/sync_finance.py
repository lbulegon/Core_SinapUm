"""
Módulo de sincronização financeira do iFood
"""
import logging
import requests
from datetime import datetime
from typing import Dict, Any, Optional
from settings import Settings
from client import IfoodAPIClient
from auth import OAuthHandler

logger = logging.getLogger(__name__)


async def sync_finance_for_store(
    settings: Settings,
    store_id: int,
    period: Optional[str] = None
) -> Dict[str, Any]:
    """
    Sincroniza dados financeiros do iFood para uma loja específica.
    
    Args:
        settings: Configurações do serviço
        store_id: ID da loja no Core
        period: Período (YYYY-MM)
    
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
            json={"kind": "financial"},
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
    
    # 4. Buscar dados financeiros do iFood
    api_client = IfoodAPIClient(settings)
    
    # TODO: Buscar token do Core e verificar expiração
    access_token = "PLACEHOLDER_TOKEN"  # Substituir por busca real no Core
    merchant_id = store_data['ifood_merchant_id']
    
    try:
        finance_data = api_client.get_financial_statements(
            access_token=access_token,
            merchant_id=merchant_id,
            period=period
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
    
    # 5. Normalizar e salvar repasses no Core
    items_ingested = 0
    errors = []
    
    payouts = finance_data.get('data', []) if isinstance(finance_data, dict) else finance_data
    
    for payout_data in payouts:
        try:
            # Normalizar repasse
            normalized_payout = {
                "store_id": store_id,
                "payout_id": payout_data.get('id') or payout_data.get('payoutId'),
                "reference_period": payout_data.get('period') or payout_data.get('referencePeriod', period or ""),
                "gross": payout_data.get('gross') or payout_data.get('grossValue', 0),
                "fees": payout_data.get('fees') or payout_data.get('feeValue', 0),
                "net": payout_data.get('net') or payout_data.get('netValue', 0),
                "channel": "ifood",
                "raw_json": payout_data,
            }
            
            # Salvar no Core
            save_response = requests.post(
                f"{settings.CORE_INTERNAL_BASE_URL}/internal/mrfoo/payouts/save",
                headers={
                    "Authorization": f"Bearer {settings.INTERNAL_API_KEY}",
                    "Content-Type": "application/json"
                },
                json=normalized_payout,
                timeout=10
            )
            
            if save_response.status_code == 200:
                items_ingested += 1
            else:
                errors.append(f"Failed to save payout {normalized_payout['payout_id']}")
        
        except Exception as e:
            errors.append(f"Error processing payout: {e}")
            logger.error(f"Error processing payout: {e}")
    
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
                    "period": period,
                    "total_payouts": len(payouts),
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

