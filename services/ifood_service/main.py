"""
iFood Service - FastAPI
Serviço para integração OAuth 2.0 e sincronização de dados do iFood.
"""
import os
import uuid
import logging
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from fastapi import FastAPI, HTTPException, Query, Request
from fastapi.responses import JSONResponse, RedirectResponse
from pydantic import BaseModel, Field
import requests
from auth import OAuthHandler
from client import IfoodAPIClient
from sync_orders import sync_orders_for_store
from sync_finance import sync_finance_for_store
from settings import Settings

# Configuração
settings = Settings()
logger = logging.getLogger(__name__)

# Inicializar FastAPI
app = FastAPI(
    title="iFood Service",
    description="Serviço de integração OAuth 2.0 e sincronização de dados do iFood",
    version="1.0.0"
)

# Handlers
oauth_handler = OAuthHandler(settings)
api_client = IfoodAPIClient(settings)


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "ifood_service",
        "timestamp": datetime.utcnow().isoformat()
    }


@app.get("/oauth/authorize-link")
async def get_authorize_link(
    store_id: int = Query(..., description="ID da loja no Core"),
    state: Optional[str] = Query(None, description="State opcional (UUID da loja)")
):
    """
    GET /oauth/authorize-link?store_id=1&state=optional
    Retorna URL de autorização OAuth do iFood.
    """
    try:
        # Buscar loja no Core
        store_response = requests.get(
            f"{settings.CORE_INTERNAL_BASE_URL}/internal/ifood/stores/{store_id}/status",
            headers={"Authorization": f"Bearer {settings.INTERNAL_API_KEY}"},
            timeout=10
        )
        
        if store_response.status_code != 200:
            raise HTTPException(status_code=404, detail="Store not found")
        
        store_data = store_response.json()
        ifood_merchant_id = store_data.get('ifood_merchant_id')
        
        if not ifood_merchant_id:
            raise HTTPException(status_code=400, detail="Store missing ifood_merchant_id")
        
        # Gerar URL de autorização
        auth_url = oauth_handler.get_authorization_url(
            state=state or str(uuid.uuid4()),
            merchant_id=ifood_merchant_id
        )
        
        return {
            "authorization_url": auth_url,
            "store_id": store_id,
            "state": state
        }
    
    except requests.RequestException as e:
        logger.error(f"Error fetching store: {e}")
        raise HTTPException(status_code=500, detail="Error connecting to Core")
    except Exception as e:
        logger.error(f"Error generating auth link: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/oauth/callback")
async def oauth_callback(
    code: str = Query(..., description="Authorization code do iFood"),
    state: str = Query(..., description="State (deve conter store_id)")
):
    """
    GET /oauth/callback?code=...&state=...
    Callback OAuth: troca code por tokens e salva no Core.
    """
    try:
        # Extrair store_id do state (ou usar state diretamente como store_id)
        # Por enquanto, assumimos que state contém o store_id
        try:
            store_id = int(state)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid state format")
        
        # Trocar code por tokens
        token_data = await oauth_handler.exchange_code_for_tokens(code)
        
        # Salvar tokens no Core
        save_response = requests.post(
            f"{settings.CORE_INTERNAL_BASE_URL}/internal/ifood/stores/{store_id}/tokens",
            headers={
                "Authorization": f"Bearer {settings.INTERNAL_API_KEY}",
                "Content-Type": "application/json"
            },
            json={
                "access_token": token_data["access_token"],
                "refresh_token": token_data["refresh_token"],
                "expires_in": token_data.get("expires_in", 3600),
                "token_type": token_data.get("token_type", "Bearer"),
                "scope": token_data.get("scope", "")
            },
            timeout=10
        )
        
        if save_response.status_code != 200:
            raise HTTPException(status_code=500, detail="Error saving tokens to Core")
        
        return {
            "success": True,
            "store_id": store_id,
            "expires_at": token_data.get("expires_at")
        }
    
    except requests.RequestException as e:
        logger.error(f"Error in OAuth callback: {e}")
        raise HTTPException(status_code=500, detail="Error connecting to Core")
    except Exception as e:
        logger.error(f"Error in OAuth callback: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/sync/orders")
async def sync_orders(
    request: Dict[str, Any]
):
    """
    POST /sync/orders
    Body: {
        "store_id": 1,
        "date_from": "2024-01-01",
        "date_to": "2024-01-31"
    }
    Sincroniza pedidos do iFood para o Core.
    """
    store_id = request.get("store_id")
    date_from = request.get("date_from")
    date_to = request.get("date_to")
    
    if not store_id:
        raise HTTPException(status_code=400, detail="store_id is required")
    
    try:
        result = await sync_orders_for_store(
            settings=settings,
            store_id=store_id,
            date_from=date_from,
            date_to=date_to
        )
        
        return result
    
    except Exception as e:
        logger.error(f"Error syncing orders: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/sync/finance")
async def sync_finance(
    request: Dict[str, Any]
):
    """
    POST /sync/finance
    Body: {
        "store_id": 1,
        "period": "2024-01"
    }
    Sincroniza dados financeiros do iFood para o Core.
    """
    store_id = request.get("store_id")
    period = request.get("period")
    
    if not store_id:
        raise HTTPException(status_code=400, detail="store_id is required")
    
    try:
        result = await sync_finance_for_store(
            settings=settings,
            store_id=store_id,
            period=period
        )
        
        return result
    
    except Exception as e:
        logger.error(f"Error syncing finance: {e}")
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=7020)

