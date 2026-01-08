"""
Provider Legacy Wrapper - Encapsula integrações existentes
==========================================================

Wrapper que encapsula as integrações WhatsApp existentes
sem alterar o código legado.

Suporta:
- app_whatsapp_gateway (EvolutionClient)
- app_whatsapp (WhatsAppRouter)
- EvolutionAPIService (Évora - se disponível)
"""
import logging
from datetime import datetime
from typing import Optional, Dict, Any
from django.conf import settings
from ..interfaces import IWhatsAppProvider
from ..schemas import ProviderResult, ProviderHealth
from ..exceptions import WhatsAppProviderNotAvailable

logger = logging.getLogger(__name__)


class ProviderLegacyWrapper(IWhatsAppProvider):
    """
    Wrapper para integrações WhatsApp existentes
    
    Tenta usar, nesta ordem:
    1. app_whatsapp_gateway.EvolutionClient (Core - multi-tenant)
    2. app_whatsapp.WhatsAppRouter (Core - gateway plugável)
    3. EvolutionAPIService (Évora - se disponível)
    
    NÃO altera código legado, apenas encapsula chamadas.
    """
    
    def __init__(self):
        """Inicializa wrapper e detecta integração disponível"""
        self._client = None
        self._client_type = None
        self._instance_key = None
        
        # Tentar detectar integração disponível
        self._detect_integration()
    
    def _detect_integration(self):
        """Detecta qual integração está disponível"""
        # 1. Tentar app_whatsapp_gateway (Core - multi-tenant)
        try:
            from app_whatsapp_gateway.clients.evolution_client import EvolutionClient
            self._client = EvolutionClient()
            self._client_type = 'evolution_client'
            self._instance_key = getattr(settings, 'EVOLUTION_INSTANCE_NAME', 'default')
            logger.info("ProviderLegacyWrapper: Usando EvolutionClient (app_whatsapp_gateway)")
            return
        except ImportError:
            pass
        
        # 2. Tentar app_whatsapp (Core - gateway plugável)
        try:
            from app_whatsapp.services.whatsapp_router import WhatsAppRouter
            router = WhatsAppRouter()
            provider = router.get_provider()
            self._client = provider
            self._client_type = 'whatsapp_router'
            self._instance_key = getattr(settings, 'EVOLUTION_INSTANCE_NAME', 'default')
            logger.info(f"ProviderLegacyWrapper: Usando WhatsAppRouter com provider {provider.name}")
            return
        except (ImportError, Exception) as e:
            logger.warning(f"ProviderLegacyWrapper: WhatsAppRouter não disponível: {e}")
        
        # 3. Tentar EvolutionAPIService (Évora - se disponível)
        try:
            from app_whatsapp_integration.evolution_service import EvolutionAPIService
            self._client = EvolutionAPIService()
            self._client_type = 'evolution_service'
            logger.info("ProviderLegacyWrapper: Usando EvolutionAPIService (Évora)")
            return
        except ImportError:
            pass
        
        # Nenhuma integração disponível
        logger.warning("ProviderLegacyWrapper: Nenhuma integração WhatsApp encontrada")
        self._client = None
        self._client_type = None
    
    @property
    def name(self) -> str:
        return "legacy"
    
    def send_text(
        self,
        to: str,
        text: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> ProviderResult:
        """Envia texto usando integração legada"""
        if not self._client:
            return ProviderResult(
                provider_name=self.name,
                status="failed",
                error="Nenhuma integração WhatsApp disponível",
                metadata=metadata or {}
            )
        
        try:
            # Normalizar número
            to_normalized = self._normalize_phone(to)
            
            # Chamar integração apropriada
            if self._client_type == 'evolution_client':
                # EvolutionClient (app_whatsapp_gateway)
                result = self._client.send_text(
                    instance_id=self._instance_key,
                    to=to_normalized,
                    text=text
                )
                
                if result.get('success'):
                    return ProviderResult(
                        provider_name=self.name,
                        status="sent",
                        message_id=result.get('message_id'),
                        raw=result,
                        metadata=metadata or {}
                    )
                else:
                    return ProviderResult(
                        provider_name=self.name,
                        status="failed",
                        error=result.get('error', 'Erro desconhecido'),
                        raw=result,
                        metadata=metadata or {}
                    )
            
            elif self._client_type == 'whatsapp_router':
                # WhatsAppRouter (app_whatsapp)
                result = self._client.send_message(
                    instance_key=self._instance_key,
                    to=to_normalized,
                    payload={'text': text},
                    correlation_id=metadata.get('correlation_id') if metadata else None
                )
                
                if result.get('success'):
                    return ProviderResult(
                        provider_name=self.name,
                        status="sent",
                        message_id=result.get('message_id'),
                        raw=result,
                        metadata=metadata or {}
                    )
                else:
                    return ProviderResult(
                        provider_name=self.name,
                        status="failed",
                        error=result.get('error', 'Erro desconhecido'),
                        raw=result,
                        metadata=metadata or {}
                    )
            
            elif self._client_type == 'evolution_service':
                # EvolutionAPIService (Évora)
                result = self._client.send_text_message(
                    phone=to_normalized,
                    message=text
                )
                
                if result.get('success'):
                    return ProviderResult(
                        provider_name=self.name,
                        status="sent",
                        message_id=str(result.get('message_id', '')),
                        raw=result,
                        metadata=metadata or {}
                    )
                else:
                    return ProviderResult(
                        provider_name=self.name,
                        status="failed",
                        error=result.get('error', 'Erro desconhecido'),
                        raw=result,
                        metadata=metadata or {}
                    )
            
            else:
                return ProviderResult(
                    provider_name=self.name,
                    status="failed",
                    error=f"Tipo de cliente desconhecido: {self._client_type}",
                    metadata=metadata or {}
                )
        
        except Exception as e:
            logger.error(f"Erro ao enviar mensagem via legacy: {e}", exc_info=True)
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
        """Envia mídia usando integração legada"""
        if not self._client:
            return ProviderResult(
                provider_name=self.name,
                status="failed",
                error="Nenhuma integração WhatsApp disponível",
                metadata=metadata or {}
            )
        
        try:
            # Normalizar número
            to_normalized = self._normalize_phone(to)
            
            # Chamar integração apropriada
            if self._client_type == 'evolution_client':
                # EvolutionClient (app_whatsapp_gateway)
                result = self._client.send_media(
                    instance_id=self._instance_key,
                    to=to_normalized,
                    media_url=media_url,
                    caption=caption or ''
                )
                
                if result.get('success'):
                    return ProviderResult(
                        provider_name=self.name,
                        status="sent",
                        message_id=result.get('message_id'),
                        raw=result,
                        metadata=metadata or {}
                    )
                else:
                    return ProviderResult(
                        provider_name=self.name,
                        status="failed",
                        error=result.get('error', 'Erro desconhecido'),
                        raw=result,
                        metadata=metadata or {}
                    )
            
            elif self._client_type == 'whatsapp_router':
                # WhatsAppRouter (app_whatsapp) - via send_message com payload
                result = self._client.send_message(
                    instance_key=self._instance_key,
                    to=to_normalized,
                    payload={
                        'media': {'url': media_url, 'caption': caption}
                    },
                    correlation_id=metadata.get('correlation_id') if metadata else None
                )
                
                if result.get('success'):
                    return ProviderResult(
                        provider_name=self.name,
                        status="sent",
                        message_id=result.get('message_id'),
                        raw=result,
                        metadata=metadata or {}
                    )
                else:
                    return ProviderResult(
                        provider_name=self.name,
                        status="failed",
                        error=result.get('error', 'Erro desconhecido'),
                        raw=result,
                        metadata=metadata or {}
                    )
            
            elif self._client_type == 'evolution_service':
                # EvolutionAPIService (Évora)
                result = self._client.send_image(
                    phone=to_normalized,
                    image_url=media_url,
                    caption=caption or ''
                )
                
                if result.get('success'):
                    return ProviderResult(
                        provider_name=self.name,
                        status="sent",
                        message_id=str(result.get('message_id', '')),
                        raw=result,
                        metadata=metadata or {}
                    )
                else:
                    return ProviderResult(
                        provider_name=self.name,
                        status="failed",
                        error=result.get('error', 'Erro desconhecido'),
                        raw=result,
                        metadata=metadata or {}
                    )
            
            else:
                return ProviderResult(
                    provider_name=self.name,
                    status="failed",
                    error=f"Tipo de cliente desconhecido: {self._client_type}",
                    metadata=metadata or {}
                )
        
        except Exception as e:
            logger.error(f"Erro ao enviar mídia via legacy: {e}", exc_info=True)
            return ProviderResult(
                provider_name=self.name,
                status="failed",
                error=str(e),
                metadata=metadata or {}
            )
    
    def healthcheck(self) -> ProviderHealth:
        """Verifica saúde da integração legada"""
        if not self._client:
            return ProviderHealth(
                provider_name=self.name,
                status="unhealthy",
                message="Nenhuma integração WhatsApp disponível",
                last_check=datetime.now()
            )
        
        try:
            # Tentar healthcheck específico do cliente
            if hasattr(self._client, 'health'):
                health_result = self._client.health()
                if isinstance(health_result, dict):
                    status_str = "healthy" if health_result.get('status') == 'ok' else "unhealthy"
                    return ProviderHealth(
                        provider_name=self.name,
                        status=status_str,
                        message=health_result.get('message', ''),
                        last_check=datetime.now(),
                        metadata={'client_type': self._client_type}
                    )
            
            # Se não tem healthcheck, assumir saudável se cliente existe
            return ProviderHealth(
                provider_name=self.name,
                status="healthy",
                message=f"Legacy integration available ({self._client_type})",
                last_check=datetime.now(),
                metadata={'client_type': self._client_type}
            )
        except Exception as e:
            return ProviderHealth(
                provider_name=self.name,
                status="unhealthy",
                message=f"Error checking health: {str(e)}",
                last_check=datetime.now(),
                metadata={'client_type': self._client_type}
            )
    
    @staticmethod
    def _normalize_phone(phone: str) -> str:
        """Normaliza número de telefone"""
        # Remove caracteres especiais
        phone = phone.replace(" ", "").replace("-", "").replace("(", "").replace(")", "")
        
        # Garante que começa com +
        if not phone.startswith("+"):
            if phone.startswith("55"):
                phone = f"+{phone}"
            else:
                # Assumir número brasileiro sem código do país
                phone = f"+55{phone}"
        
        return phone
