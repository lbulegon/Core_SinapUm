"""
Módulo de autenticação OAuth 2.0 com iFood
"""
import logging
import requests
from typing import Dict, Any, Optional
from datetime import datetime, timedelta
from settings import Settings

logger = logging.getLogger(__name__)


class OAuthHandler:
    """Handler para fluxo OAuth 2.0 do iFood"""
    
    def __init__(self, settings: Settings):
        self.settings = settings
        self.client_id = settings.IFOOD_CLIENT_ID
        self.client_secret = settings.IFOOD_CLIENT_SECRET
        self.auth_base_url = settings.IFOOD_AUTH_BASE_URL
        self.redirect_uri = settings.IFOOD_REDIRECT_URI
    
    def get_authorization_url(self, state: str, merchant_id: Optional[str] = None) -> str:
        """
        Gera URL de autorização OAuth.
        
        Args:
            state: State para controle de fluxo (geralmente store_id ou UUID)
            merchant_id: ID do merchant no iFood (opcional)
        
        Returns:
            URL de autorização
        """
        params = {
            "client_id": self.client_id,
            "response_type": "code",
            "redirect_uri": self.redirect_uri,
            "scope": "orders finance catalog",
            "state": state,
        }
        
        if merchant_id:
            params["merchant_id"] = merchant_id
        
        # Construir URL
        query_string = "&".join([f"{k}={v}" for k, v in params.items()])
        auth_url = f"{self.auth_base_url}/oauth/authorize?{query_string}"
        
        return auth_url
    
    async def exchange_code_for_tokens(self, code: str) -> Dict[str, Any]:
        """
        Troca authorization code por access_token e refresh_token.
        
        Args:
            code: Authorization code recebido no callback
        
        Returns:
            Dict com tokens e metadados
        """
        token_url = f"{self.auth_base_url}/oauth/token"
        
        data = {
            "grant_type": "authorization_code",
            "code": code,
            "redirect_uri": self.redirect_uri,
            "client_id": self.client_id,
            "client_secret": self.client_secret,
        }
        
        try:
            response = requests.post(token_url, data=data, timeout=30)
            response.raise_for_status()
            
            token_data = response.json()
            
            # Calcular expires_at
            expires_in = token_data.get("expires_in", 3600)
            expires_at = datetime.utcnow() + timedelta(seconds=expires_in)
            
            return {
                "access_token": token_data["access_token"],
                "refresh_token": token_data["refresh_token"],
                "token_type": token_data.get("token_type", "Bearer"),
                "expires_in": expires_in,
                "expires_at": expires_at.isoformat(),
                "scope": token_data.get("scope", ""),
            }
        
        except requests.RequestException as e:
            logger.error(f"Error exchanging code for tokens: {e}")
            raise Exception(f"Failed to exchange code for tokens: {e}")
    
    async def refresh_access_token(self, refresh_token: str) -> Dict[str, Any]:
        """
        Renova access_token usando refresh_token.
        
        Args:
            refresh_token: Refresh token válido
        
        Returns:
            Dict com novos tokens
        """
        token_url = f"{self.auth_base_url}/oauth/token"
        
        data = {
            "grant_type": "refresh_token",
            "refresh_token": refresh_token,
            "client_id": self.client_id,
            "client_secret": self.client_secret,
        }
        
        try:
            response = requests.post(token_url, data=data, timeout=30)
            response.raise_for_status()
            
            token_data = response.json()
            
            # Calcular expires_at
            expires_in = token_data.get("expires_in", 3600)
            expires_at = datetime.utcnow() + timedelta(seconds=expires_in)
            
            return {
                "access_token": token_data["access_token"],
                "refresh_token": token_data.get("refresh_token", refresh_token),  # iFood pode retornar novo refresh_token
                "token_type": token_data.get("token_type", "Bearer"),
                "expires_in": expires_in,
                "expires_at": expires_at.isoformat(),
                "scope": token_data.get("scope", ""),
            }
        
        except requests.RequestException as e:
            logger.error(f"Error refreshing token: {e}")
            raise Exception(f"Failed to refresh token: {e}")

