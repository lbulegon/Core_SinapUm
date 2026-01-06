"""
Provider simulado para desenvolvimento sem WhatsApp real
"""
import hashlib
import base64
from typing import Dict, Any, Optional
from django.http import HttpRequest
from app_whatsapp.domain.provider_contract import IWhatsAppProvider
from app_whatsapp.domain.events import EventType
from app_whatsapp.services.event_bus import EventBus
from app_whatsapp.models import AppWhatsappInstance


class ProviderSimulated(IWhatsAppProvider):
    """Provider simulado para desenvolvimento sem WhatsApp real"""
    
    @property
    def name(self) -> str:
        return "simulated"
    
    def create_instance(self, instance_key: str) -> Dict[str, Any]:
        """Cria instância simulada (sempre conectável)"""
        instance, created = AppWhatsappInstance.objects.get_or_create(
            instance_key=instance_key,
            defaults={
                "provider": self.name,
                "status": "connecting",
            }
        )
        
        EventBus.emit(
            provider=self.name,
            instance_key=instance_key,
            event_type=EventType.INSTANCE_CREATED,
            data={"status": instance.status},
        )
        
        return {
            "success": True,
            "instance_key": instance_key,
            "status": instance.status,
        }
    
    def get_qr(self, instance_key: str) -> Dict[str, Any]:
        """Gera QR fake determinístico"""
        try:
            instance = AppWhatsappInstance.objects.get(instance_key=instance_key)
        except AppWhatsappInstance.DoesNotExist:
            return {"count": 0, "qr_code": None}
        
        # QR fake baseado no instance_key (determinístico)
        qr_data = f"SIMULATED_QR_{instance_key}"
        qr_hash = hashlib.md5(qr_data.encode()).hexdigest()
        qr_code = base64.b64encode(qr_hash.encode()).decode()[:32]
        
        instance.last_qr = qr_code
        instance.save()
        
        EventBus.emit(
            provider=self.name,
            instance_key=instance_key,
            event_type=EventType.QR_UPDATED,
            data={"qr_code": qr_code, "count": 1},
        )
        
        return {
            "count": 1,
            "qr_code": qr_code,
            "base64": f"data:image/png;base64,{qr_code}",
        }
    
    def send_message(
        self,
        instance_key: str,
        to: str,
        payload: Dict[str, Any],
        correlation_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Simula envio de mensagem"""
        message_id = f"sim_{hashlib.md5(f'{instance_key}{to}'.encode()).hexdigest()[:16]}"
        
        EventBus.emit(
            provider=self.name,
            instance_key=instance_key,
            event_type=EventType.MESSAGE_OUT,
            data={
                "to": to,
                "message_id": message_id,
                "payload": payload,
            },
            correlation_id=correlation_id,
        )
        
        return {
            "success": True,
            "message_id": message_id,
        }
    
    def health(self) -> Dict[str, Any]:
        return {"status": "ok", "message": "Simulated provider is always healthy"}
    
    def handle_inbound_webhook(self, request: HttpRequest) -> Dict[str, Any]:
        """Simulado não usa webhook real"""
        return {"success": False, "message": "Simulated provider does not use webhooks"}
    
    def simulate_scan(self, instance_key: str) -> Dict[str, Any]:
        """Método especial: simula escaneamento do QR"""
        try:
            instance = AppWhatsappInstance.objects.get(instance_key=instance_key)
            instance.status = "connected"
            instance.save()
            
            EventBus.emit(
                provider=self.name,
                instance_key=instance_key,
                event_type=EventType.CONNECTED,
                data={"status": "connected"},
            )
            
            return {"success": True, "status": "connected"}
        except AppWhatsappInstance.DoesNotExist:
            return {"success": False, "error": "Instance not found"}
    
    def simulate_disconnect(self, instance_key: str) -> Dict[str, Any]:
        """Método especial: simula desconexão"""
        try:
            instance = AppWhatsappInstance.objects.get(instance_key=instance_key)
            instance.status = "closed"
            instance.save()
            
            EventBus.emit(
                provider=self.name,
                instance_key=instance_key,
                event_type=EventType.DISCONNECTED,
                data={"status": "closed"},
            )
            
            return {"success": True, "status": "closed"}
        except AppWhatsappInstance.DoesNotExist:
            return {"success": False, "error": "Instance not found"}
    
    def simulate_inbound_message(
        self,
        instance_key: str,
        from_number: str,
        text: str,
        shopper_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Método especial: simula mensagem recebida"""
        EventBus.emit(
            provider=self.name,
            instance_key=instance_key,
            event_type=EventType.MESSAGE_IN,
            data={
                "from": from_number,
                "text": text,
            },
            shopper_id=shopper_id,
        )
        
        return {
            "success": True,
            "message": "Inbound message simulated",
        }
