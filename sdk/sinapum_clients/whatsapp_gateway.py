"""WhatsApp Gateway Client - Envio de mensagens"""
import logging
from typing import Any, Dict, Optional
import requests

logger = logging.getLogger(__name__)


class WhatsAppGatewayClient:
    """Cliente para WhatsApp Gateway Service (Baileys)"""

    def __init__(
        self,
        base_url: str,
        api_key: str = "",
        instance_id: str = "default",
        timeout: int = 30,
    ):
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.instance_id = instance_id
        self.timeout = timeout

    def _headers(self) -> Dict[str, str]:
        h = {"Content-Type": "application/json", "X-API-Key": self.api_key}
        if self.instance_id:
            h["X-Instance-Id"] = self.instance_id
        return h

    def send_text(
        self,
        to: str,
        text: str,
    ) -> Dict[str, Any]:
        """Envia mensagem de texto"""
        url = f"{self.base_url}/v1/send/text"
        phone = to.replace("+", "").replace(" ", "").replace("-", "")
        payload = {"to": phone, "text": text}
        try:
            r = requests.post(url, json=payload, headers=self._headers(), timeout=self.timeout)
            data = r.json() if r.content else {}
            if r.status_code == 200:
                return {"success": True, "message_id": data.get("message_id"), **data}
            return {"success": False, "error": data.get("error", r.text)}
        except requests.RequestException as e:
            logger.error(f"WhatsApp Gateway error: {e}")
            return {"success": False, "error": str(e)}

    def send_image(
        self,
        to: str,
        image_url: str,
        caption: str = "",
    ) -> Dict[str, Any]:
        """Envia imagem"""
        url = f"{self.base_url}/v1/send/image"
        phone = to.replace("+", "").replace(" ", "").replace("-", "")
        payload = {"to": phone, "image_url": image_url, "caption": caption}
        try:
            r = requests.post(url, json=payload, headers=self._headers(), timeout=self.timeout)
            data = r.json() if r.content else {}
            if r.status_code == 200:
                return {"success": True, **data}
            return {"success": False, "error": data.get("error", r.text)}
        except requests.RequestException as e:
            logger.error(f"WhatsApp Gateway error: {e}")
            return {"success": False, "error": str(e)}
