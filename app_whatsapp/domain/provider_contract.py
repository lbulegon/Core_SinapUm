"""
Contrato único para todos os providers WhatsApp
"""
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from django.http import HttpRequest


class IWhatsAppProvider(ABC):
    """Contrato único para todos os providers WhatsApp"""
    
    @property
    @abstractmethod
    def name(self) -> str:
        """Nome do provider (simulated, cloud, baileys, evolution)"""
        pass
    
    @abstractmethod
    def create_instance(self, instance_key: str) -> Dict[str, Any]:
        """
        Cria uma nova instância WhatsApp.
        
        Args:
            instance_key: Chave única da instância
        
        Returns:
            {"success": bool, "instance_key": str, "status": str}
        
        Deve emitir evento INSTANCE_CREATED via EventBus.
        """
        pass
    
    @abstractmethod
    def get_qr(self, instance_key: str) -> Dict[str, Any]:
        """
        Obtém QR code da instância (se aplicável).
        
        Args:
            instance_key: Chave da instância
        
        Returns:
            {"count": int, "qr_code": str, "base64": str (opcional)}
        
        Deve emitir evento QR_UPDATED se QR mudou.
        """
        pass
    
    @abstractmethod
    def send_message(
        self,
        instance_key: str,
        to: str,
        payload: Dict[str, Any],
        correlation_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Envia mensagem.
        
        Args:
            instance_key: Chave da instância
            to: Número de destino
            payload: {"text": str, "media": dict (opcional), "buttons": list (opcional)}
            correlation_id: ID de correlação (opcional)
        
        Returns:
            {"success": bool, "message_id": str}
        
        Deve emitir evento MESSAGE_OUT via EventBus.
        """
        pass
    
    @abstractmethod
    def health(self) -> Dict[str, Any]:
        """
        Verifica saúde do provider.
        
        Returns:
            {"status": "ok|error", "message": str}
        """
        pass
    
    @abstractmethod
    def handle_inbound_webhook(self, request: HttpRequest) -> Dict[str, Any]:
        """
        Processa webhook de entrada do provider.
        
        Args:
            request: Request HTTP do webhook
        
        Returns:
            {"success": bool, "events": list}
        
        Deve emitir eventos MESSAGE_IN, DELIVERY, etc via EventBus.
        """
        pass
