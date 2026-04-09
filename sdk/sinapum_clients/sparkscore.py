"""SparkScore Client - Score de conteúdo"""
import logging
from typing import Any, Dict, Optional
import requests

logger = logging.getLogger(__name__)


class SparkScoreClient:
    """Cliente para SparkScore Service"""

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

    def score_content(
        self,
        content: str,
        content_type: str = "text",
    ) -> Dict[str, Any]:
        """Calcula score de uma peça de conteúdo"""
        url = f"{self.base_url}/api/score/"
        payload = {"content": content, "content_type": content_type}
        try:
            r = requests.post(url, json=payload, headers=self._headers(), timeout=self.timeout)
            r.raise_for_status()
            return r.json()
        except requests.RequestException as e:
            logger.error(f"SparkScore error: {e}")
            return {"success": False, "error": str(e), "score": 0}
