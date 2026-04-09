"""OpenMind Client - Análise de imagens e IA"""
import logging
from typing import Any, Dict, Optional
import requests

logger = logging.getLogger(__name__)


class OpenMindClient:
    """Cliente para OpenMind Service"""

    def __init__(
        self,
        base_url: str,
        token: str = "",
        timeout: int = 30,
    ):
        self.base_url = base_url.rstrip("/")
        self.token = token
        self.timeout = timeout

    def _headers(self) -> Dict[str, str]:
        h = {"Content-Type": "application/json"}
        if self.token:
            h["Authorization"] = f"Bearer {self.token}"
        return h

    def analyze_image(
        self,
        image_url: str,
        prompt: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Analisa imagem de produto"""
        url = f"{self.base_url}/api/v1/analyze-product-image/"
        payload = {"image_url": image_url, "prompt": prompt or ""}
        try:
            r = requests.post(url, json=payload, headers=self._headers(), timeout=self.timeout)
            r.raise_for_status()
            return r.json()
        except requests.RequestException as e:
            logger.error(f"OpenMind error: {e}")
            return {"success": False, "error": str(e)}
