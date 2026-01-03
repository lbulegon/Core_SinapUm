"""
Cliente HTTP para APIs do iFood
"""
import logging
import requests
from typing import Dict, Any, Optional, List
from settings import Settings

logger = logging.getLogger(__name__)


class IfoodAPIClient:
    """Cliente para consumir APIs do iFood"""
    
    def __init__(self, settings: Settings):
        self.settings = settings
        self.api_base_url = settings.IFOOD_API_BASE_URL
    
    def _get_headers(self, access_token: str) -> Dict[str, str]:
        """Retorna headers padrão para requisições"""
        return {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json",
            "Accept": "application/json",
        }
    
    def get_orders(
        self,
        access_token: str,
        merchant_id: str,
        date_from: Optional[str] = None,
        date_to: Optional[str] = None,
        page: int = 0,
        size: int = 100
    ) -> Dict[str, Any]:
        """
        Busca pedidos do iFood.
        
        Args:
            access_token: Access token OAuth
            merchant_id: ID do merchant
            date_from: Data inicial (YYYY-MM-DD)
            date_to: Data final (YYYY-MM-DD)
            page: Página (0-indexed)
            size: Tamanho da página
        
        Returns:
            Dict com lista de pedidos
        """
        url = f"{self.api_base_url}/v1.0/orders"
        
        params = {
            "merchantId": merchant_id,
            "page": page,
            "size": size,
        }
        
        if date_from:
            params["startDate"] = date_from
        if date_to:
            params["endDate"] = date_to
        
        try:
            response = requests.get(
                url,
                headers=self._get_headers(access_token),
                params=params,
                timeout=30
            )
            response.raise_for_status()
            return response.json()
        
        except requests.RequestException as e:
            logger.error(f"Error fetching orders: {e}")
            raise Exception(f"Failed to fetch orders: {e}")
    
    def get_financial_statements(
        self,
        access_token: str,
        merchant_id: str,
        period: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Busca extratos financeiros do iFood.
        
        Args:
            access_token: Access token OAuth
            merchant_id: ID do merchant
            period: Período (YYYY-MM)
        
        Returns:
            Dict com dados financeiros
        """
        url = f"{self.api_base_url}/v1.0/financial/statements"
        
        params = {
            "merchantId": merchant_id,
        }
        
        if period:
            params["period"] = period
        
        try:
            response = requests.get(
                url,
                headers=self._get_headers(access_token),
                params=params,
                timeout=30
            )
            response.raise_for_status()
            return response.json()
        
        except requests.RequestException as e:
            logger.error(f"Error fetching financial statements: {e}")
            raise Exception(f"Failed to fetch financial statements: {e}")
    
    def get_catalog(
        self,
        access_token: str,
        merchant_id: str
    ) -> Dict[str, Any]:
        """
        Busca catálogo do iFood.
        
        Args:
            access_token: Access token OAuth
            merchant_id: ID do merchant
        
        Returns:
            Dict com catálogo
        """
        url = f"{self.api_base_url}/v1.0/catalog"
        
        params = {
            "merchantId": merchant_id,
        }
        
        try:
            response = requests.get(
                url,
                headers=self._get_headers(access_token),
                params=params,
                timeout=30
            )
            response.raise_for_status()
            return response.json()
        
        except requests.RequestException as e:
            logger.error(f"Error fetching catalog: {e}")
            raise Exception(f"Failed to fetch catalog: {e}")

