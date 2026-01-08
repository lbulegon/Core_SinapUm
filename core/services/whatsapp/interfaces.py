"""
Interfaces - WhatsApp Gateway
==============================

Interface padrão para providers WhatsApp.
Focada em envio de mensagens (não instâncias, QR codes, etc.).
"""
from abc import ABC, abstractmethod
from typing import Optional, Dict, Any
from .schemas import ProviderResult, ProviderHealth


class IWhatsAppProvider(ABC):
    """
    Interface padrão para providers WhatsApp
    
    Focada em envio de mensagens. Não inclui gerenciamento de instâncias,
    QR codes, etc. (isso fica nos providers específicos se necessário).
    """
    
    @property
    @abstractmethod
    def name(self) -> str:
        """
        Nome do provider
        
        Returns:
            Nome único do provider (ex: "legacy", "simulated", "noop", "evolution")
        """
        pass
    
    @abstractmethod
    def send_text(
        self,
        to: str,
        text: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> ProviderResult:
        """
        Envia mensagem de texto
        
        Args:
            to: Número de destino (formato: 5511999999999 ou +5511999999999)
            text: Texto da mensagem
            metadata: Metadados adicionais (shopper_id, skm_id, correlation_id, etc.)
        
        Returns:
            ProviderResult com resultado da operação
        """
        pass
    
    @abstractmethod
    def send_media(
        self,
        to: str,
        media_url: str,
        caption: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> ProviderResult:
        """
        Envia mídia (imagem, vídeo, etc.)
        
        Args:
            to: Número de destino
            media_url: URL da mídia
            caption: Legenda (opcional)
            metadata: Metadados adicionais
        
        Returns:
            ProviderResult com resultado da operação
        """
        pass
    
    def send_template(
        self,
        to: str,
        template_name: str,
        template_params: Optional[Dict[str, Any]] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> ProviderResult:
        """
        Envia template (opcional - alguns providers não suportam)
        
        Args:
            to: Número de destino
            template_name: Nome do template
            template_params: Parâmetros do template
            metadata: Metadados adicionais
        
        Returns:
            ProviderResult com resultado da operação
        
        Raises:
            NotImplementedError: Se provider não suporta templates
        """
        raise NotImplementedError(f"Provider {self.name} não suporta templates")
    
    @abstractmethod
    def healthcheck(self) -> ProviderHealth:
        """
        Verifica saúde do provider
        
        Returns:
            ProviderHealth com status do provider
        """
        pass
