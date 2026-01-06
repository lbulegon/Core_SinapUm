"""
Stub para Cloud API (Fase A2)
"""
from typing import Dict, Any, Optional
from django.http import HttpRequest
from app_whatsapp.domain.provider_contract import IWhatsAppProvider
from app_whatsapp.domain.events import EventType
from app_whatsapp.services.event_bus import EventBus


class ProviderCloud(IWhatsAppProvider):
    """Stub para Cloud API (Fase A2)"""
    
    @property
    def name(self) -> str:
        return "cloud"
    
    def create_instance(self, instance_key: str) -> Dict[str, Any]:
        EventBus.emit(
            provider=self.name,
            instance_key=instance_key,
            event_type=EventType.ERROR,
            data={"error": "Provider cloud not implemented yet"},
        )
        raise NotImplementedError("Cloud provider not implemented")
    
    def get_qr(self, instance_key: str) -> Dict[str, Any]:
        EventBus.emit(
            provider=self.name,
            instance_key=instance_key,
            event_type=EventType.ERROR,
            data={"error": "Provider cloud not implemented yet"},
        )
        raise NotImplementedError("Cloud provider not implemented")
    
    def send_message(
        self,
        instance_key: str,
        to: str,
        payload: Dict[str, Any],
        correlation_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        EventBus.emit(
            provider=self.name,
            instance_key=instance_key,
            event_type=EventType.ERROR,
            data={"error": "Provider cloud not implemented yet"},
        )
        raise NotImplementedError("Cloud provider not implemented")
    
    def health(self) -> Dict[str, Any]:
        return {"status": "error", "message": "Cloud provider not implemented yet"}
    
    def handle_inbound_webhook(self, request: HttpRequest) -> Dict[str, Any]:
        EventBus.emit(
            provider=self.name,
            instance_key="unknown",
            event_type=EventType.ERROR,
            data={"error": "Provider cloud not implemented yet"},
        )
        raise NotImplementedError("Cloud provider not implemented")
