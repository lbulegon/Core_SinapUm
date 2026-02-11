import os
import requests
from typing import Any, Dict, Optional


class WhatsAppGatewayError(RuntimeError):
    pass


class WhatsAppGatewayClient:
    """
    Cliente HTTP simples para seu whatsapp_gateway_service.
    Mantém desacoplado: só envia comando de saída.
    """

    def __init__(self) -> None:
        self.base_url = os.getenv("WHATSAPP_GATEWAY_URL", "").rstrip("/")
        self.api_key = os.getenv("SINAPUM_WHATSAPP_GATEWAY_API_KEY", "")
        self.timeout = float(os.getenv("WHATSAPP_GATEWAY_TIMEOUT", "6"))

        if not self.base_url:
            raise WhatsAppGatewayError("WHATSAPP_GATEWAY_URL não configurada")

    def _headers(self) -> Dict[str, str]:
        h = {"Content-Type": "application/json"}
        if self.api_key:
            h["Authorization"] = f"Bearer {self.api_key}"
        return h

    def send_message(self, to: str, text: str, meta: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        POST {WHATSAPP_GATEWAY_URL}/messages/send
        body: { "to": "...", "text": "...", "meta": {...} }
        """
        url = f"{self.base_url}/messages/send"
        payload: Dict[str, Any] = {"to": to, "text": text}
        if meta:
            payload["meta"] = meta

        resp = requests.post(url, json=payload, headers=self._headers(), timeout=self.timeout)
        if resp.status_code >= 400:
            raise WhatsAppGatewayError(f"Gateway error {resp.status_code}: {resp.text[:500]}")
        try:
            return resp.json()
        except Exception:
            return {"status": "ok", "raw": resp.text}
