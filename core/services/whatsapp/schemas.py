"""
Schemas - WhatsApp Gateway
==========================

Schemas padronizados para resultados e respostas do gateway.
"""
from dataclasses import dataclass
from typing import Optional, Dict, Any
from datetime import datetime


@dataclass
class ProviderResult:
    """
    Resultado padronizado de operação do provider
    
    Attributes:
        provider_name: Nome do provider usado
        message_id: ID da mensagem (se disponível)
        status: Status da operação ("queued", "sent", "failed")
        raw: Payload bruto retornado pelo provider (opcional)
        error: Mensagem de erro (se status="failed")
        metadata: Metadados adicionais
    """
    provider_name: str
    status: str  # "queued", "sent", "failed"
    message_id: Optional[str] = None
    raw: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
    
    def is_success(self) -> bool:
        """Verifica se operação foi bem-sucedida"""
        return self.status in ("queued", "sent")
    
    def is_failed(self) -> bool:
        """Verifica se operação falhou"""
        return self.status == "failed"


@dataclass
class ProviderHealth:
    """
    Status de saúde do provider
    
    Attributes:
        provider_name: Nome do provider
        status: Status ("healthy", "degraded", "unhealthy")
        message: Mensagem descritiva
        last_check: Timestamp da última verificação
        metadata: Metadados adicionais
    """
    provider_name: str
    status: str  # "healthy", "degraded", "unhealthy"
    message: str
    last_check: datetime
    metadata: Optional[Dict[str, Any]] = None
    
    def is_healthy(self) -> bool:
        """Verifica se provider está saudável"""
        return self.status == "healthy"
