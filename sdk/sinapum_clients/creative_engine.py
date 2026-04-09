"""Creative Engine Client - Geração de criativos"""
import logging
from typing import Any, Dict, Optional
import requests

logger = logging.getLogger(__name__)


class CreativeEngineClient:
    """Cliente para Creative Engine Service"""

    def __init__(
        self,
        base_url: str,
        api_token: str = "",
        timeout: int = 15,
    ):
        self.base_url = base_url.rstrip("/")
        self.api_token = api_token
        self.timeout = timeout

    def _headers(self) -> Dict[str, str]:
        h = {"Content-Type": "application/json"}
        if self.api_token:
            h["Authorization"] = f"Bearer {self.api_token}"
        return h

    def generate_text(
        self,
        prompt: str,
        context: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Gera texto criativo"""
        url = f"{self.base_url}/api/creative-engine/generate-text/"
        payload = {"prompt": prompt, "context": context or {}}
        try:
            r = requests.post(url, json=payload, headers=self._headers(), timeout=self.timeout)
            r.raise_for_status()
            return r.json()
        except requests.RequestException as e:
            logger.error(f"CreativeEngine error: {e}")
            return {"success": False, "error": str(e)}
