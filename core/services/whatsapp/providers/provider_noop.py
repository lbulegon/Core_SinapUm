"""
Provider NoOp - Não faz nada, apenas loga
==========================================

Provider para ambientes de desenvolvimento onde não queremos
enviar mensagens reais, apenas logar o que seria enviado.
"""
import logging
from datetime import datetime
from typing import Optional, Dict, Any
from ..interfaces import IWhatsAppProvider
from ..schemas import ProviderResult, ProviderHealth

logger = logging.getLogger(__name__)


class ProviderNoOp(IWhatsAppProvider):
    """
    Provider que não envia nada, apenas loga
    
    Útil para:
    - Desenvolvimento local
    - Testes
    - Ambientes onde WhatsApp não está disponível
    """
    
    @property
    def name(self) -> str:
        return "noop"
    
    def send_text(
        self,
        to: str,
        text: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> ProviderResult:
        """Loga mensagem sem enviar"""
        logger.info(
            f"[WhatsApp NoOp] Enviaria mensagem de texto",
            extra={
                'to': to,
                'text_length': len(text),
                'text_preview': text[:100] + '...' if len(text) > 100 else text,
                'metadata': metadata or {}
            }
        )
        
        return ProviderResult(
            provider_name=self.name,
            status="sent",  # Simula sucesso
            message_id=f"noop_{datetime.now().timestamp()}",
            metadata={
                'logged': True,
                'timestamp': datetime.now().isoformat(),
                **({} if metadata is None else metadata)
            }
        )
    
    def send_media(
        self,
        to: str,
        media_url: str,
        caption: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> ProviderResult:
        """Loga mídia sem enviar"""
        logger.info(
            f"[WhatsApp NoOp] Enviaria mídia",
            extra={
                'to': to,
                'media_url': media_url,
                'caption': caption,
                'metadata': metadata or {}
            }
        )
        
        return ProviderResult(
            provider_name=self.name,
            status="sent",  # Simula sucesso
            message_id=f"noop_{datetime.now().timestamp()}",
            metadata={
                'logged': True,
                'timestamp': datetime.now().isoformat(),
                **({} if metadata is None else metadata)
            }
        )
    
    def healthcheck(self) -> ProviderHealth:
        """Sempre saudável (não depende de nada externo)"""
        return ProviderHealth(
            provider_name=self.name,
            status="healthy",
            message="NoOp provider is always healthy",
            last_check=datetime.now()
        )
