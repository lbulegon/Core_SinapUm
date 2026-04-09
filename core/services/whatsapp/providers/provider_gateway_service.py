"""
Provider Gateway Service - WhatsApp Gateway Service (Node.js + Baileys)
========================================================================

Provider que usa o WhatsApp Gateway Service via HTTP.
Serviço Node.js em /root/Core_SinapUm/services/whatsapp_gateway_service
"""
import logging
from datetime import datetime
from typing import Optional, Dict, Any

from ..interfaces import IWhatsAppProvider
from ..schemas import ProviderResult, ProviderHealth

logger = logging.getLogger(__name__)


class ProviderGatewayService(IWhatsAppProvider):
    """
    Provider que usa o WhatsApp Gateway Service (porta 8007)
    Comunicação via HTTP com o serviço Node.js + Baileys
    """
    
    _client = None
    
    @property
    def name(self) -> str:
        return "gateway_service"
    
    def _get_client(self):
        """Lazy load do WhatsAppGatewayClient"""
        if self._client is None:
            from core.services.whatsapp_gateway_client import get_whatsapp_gateway_client
            self._client = get_whatsapp_gateway_client()
        return self._client
    
    def send_text(
        self,
        to: str,
        text: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> ProviderResult:
        """Envia texto via WhatsApp Gateway Service"""
        try:
            client = self._get_client()
            to_normalized = self._normalize_phone(to)
            result = client.send_text(to=to_normalized, text=text)
            
            if result.get('success') or result.get('status') == 'sent':
                return ProviderResult(
                    provider_name=self.name,
                    status="sent",
                    message_id=result.get('message_id'),
                    raw=result,
                    metadata=metadata or {}
                )
            return ProviderResult(
                provider_name=self.name,
                status="failed",
                error=result.get('error', 'Erro desconhecido'),
                raw=result,
                metadata=metadata or {}
            )
        except Exception as e:
            logger.error(f"Erro ao enviar mensagem via gateway: {e}", exc_info=True)
            return ProviderResult(
                provider_name=self.name,
                status="failed",
                error=str(e),
                metadata=metadata or {}
            )
    
    def send_media(
        self,
        to: str,
        media_url: str,
        caption: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> ProviderResult:
        """Envia mídia via WhatsApp Gateway Service"""
        try:
            client = self._get_client()
            to_normalized = self._normalize_phone(to)
            result = client.send_image(to=to_normalized, image_url=media_url, caption=caption or '')
            
            if result.get('success') or result.get('status') == 'sent':
                return ProviderResult(
                    provider_name=self.name,
                    status="sent",
                    message_id=result.get('message_id'),
                    raw=result,
                    metadata=metadata or {}
                )
            return ProviderResult(
                provider_name=self.name,
                status="failed",
                error=result.get('error', 'Erro desconhecido'),
                raw=result,
                metadata=metadata or {}
            )
        except Exception as e:
            logger.error(f"Erro ao enviar mídia via gateway: {e}", exc_info=True)
            return ProviderResult(
                provider_name=self.name,
                status="failed",
                error=str(e),
                metadata=metadata or {}
            )
    
    def healthcheck(self) -> ProviderHealth:
        """Verifica saúde do WhatsApp Gateway Service"""
        try:
            client = self._get_client()
            result = client.healthcheck()
            status_ok = result.get('status') == 'ok' or result.get('whatsapp', {}).get('connected')
            return ProviderHealth(
                provider_name=self.name,
                status="healthy" if status_ok else "degraded",
                message=result.get('error', 'Gateway disponível') if not status_ok else 'Gateway operacional',
                last_check=datetime.now(),
                metadata={'raw': result}
            )
        except Exception as e:
            return ProviderHealth(
                provider_name=self.name,
                status="unhealthy",
                message=str(e),
                last_check=datetime.now()
            )
    
    @staticmethod
    def _normalize_phone(phone: str) -> str:
        """Normaliza número de telefone"""
        phone = phone.replace(" ", "").replace("-", "").replace("(", "").replace(")", "").replace("+", "")
        if not phone.startswith("55") and len(phone) <= 11:
            phone = "55" + phone.lstrip("0")
        return phone
