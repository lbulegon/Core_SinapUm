"""ShopperBot Client - IA vendedora"""
import logging
from typing import Any, Dict, Optional
import requests

logger = logging.getLogger(__name__)


class ShopperBotClient:
    """Cliente para ShopperBot Service"""

    def __init__(
        self,
        base_url: str,
        api_key: str = "",
        timeout: int = 10,
    ):
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.timeout = timeout

    def _headers(self) -> Dict[str, str]:
        h = {"Content-Type": "application/json"}
        if self.api_key:
            h["X-API-Key"] = self.api_key
        return h

    def process_message(
        self,
        message: str,
        context: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Processa mensagem e retorna intenção/recomendação"""
        url = f"{self.base_url}/api/process/"
        payload = {"message": message, "context": context or {}}
        try:
            r = requests.post(url, json=payload, headers=self._headers(), timeout=self.timeout)
            r.raise_for_status()
            return r.json()
        except requests.RequestException as e:
            logger.error(f"ShopperBot error: {e}")
            return {"success": False, "error": str(e)}
