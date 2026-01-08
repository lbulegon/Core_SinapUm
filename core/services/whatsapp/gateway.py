"""
WhatsApp Gateway - Camada de Abstração Padrão
==============================================

Gateway que escolhe provider ativo e expõe interface padronizada.
Nunca quebra: se provider falhar, retorna erro padronizado e loga.
"""
import logging
from datetime import datetime
from typing import Optional, Dict, Any
from django.conf import settings

from .interfaces import IWhatsAppProvider
from .schemas import ProviderResult, ProviderHealth
from .exceptions import WhatsAppProviderError, WhatsAppProviderNotAvailable
from .settings import (
    get_whatsapp_provider,
    is_whatsapp_send_enabled,
    is_whatsapp_shadow_mode,
    get_enabled_shoppers
)

logger = logging.getLogger(__name__)


class WhatsAppGateway:
    """
    Gateway WhatsApp - Camada de abstração padrão
    
    Responsável por:
    - Escolher provider ativo por feature flag/env var
    - Expor métodos padronizados (send_text, send_media)
    - Nunca quebrar: se provider falhar, retorna erro padronizado
    - Logging estruturado com metadata (shopper_id, skm_id, etc.)
    """
    
    _instance: Optional['WhatsAppGateway'] = None
    _provider: Optional[IWhatsAppProvider] = None
    
    def __new__(cls):
        """Singleton pattern"""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def _get_provider(self) -> IWhatsAppProvider:
        """
        Obtém provider ativo (lazy initialization)
        
        Returns:
            Instância do provider ativo
        
        Raises:
            WhatsAppProviderNotAvailable: Se provider não está disponível
        """
        if self._provider is None:
            provider_name = get_whatsapp_provider()
            
            try:
                if provider_name == 'legacy':
                    from .providers.provider_legacy_wrapper import ProviderLegacyWrapper
                    self._provider = ProviderLegacyWrapper()
                
                elif provider_name == 'simulated':
                    from .providers.provider_simulated import ProviderSimulated
                    self._provider = ProviderSimulated()
                
                elif provider_name == 'noop':
                    from .providers.provider_noop import ProviderNoOp
                    self._provider = ProviderNoOp()
                
                elif provider_name == 'evolution':
                    # Futuro: ProviderEvolution direto (não wrapper)
                    # Por enquanto, usar legacy_wrapper
                    logger.warning("Provider 'evolution' não implementado, usando 'legacy'")
                    from .providers.provider_legacy_wrapper import ProviderLegacyWrapper
                    self._provider = ProviderLegacyWrapper()
                
                elif provider_name == 'cloud':
                    # Futuro: ProviderCloud direto
                    logger.warning("Provider 'cloud' não implementado, usando 'legacy'")
                    from .providers.provider_legacy_wrapper import ProviderLegacyWrapper
                    self._provider = ProviderLegacyWrapper()
                
                elif provider_name == 'baileys':
                    # Futuro: ProviderBaileys direto
                    logger.warning("Provider 'baileys' não implementado, usando 'legacy'")
                    from .providers.provider_legacy_wrapper import ProviderLegacyWrapper
                    self._provider = ProviderLegacyWrapper()
                
                else:
                    raise ValueError(f"Provider desconhecido: {provider_name}")
                
                logger.info(f"WhatsAppGateway: Provider '{provider_name}' inicializado")
            
            except ImportError as e:
                logger.error(f"Erro ao importar provider '{provider_name}': {e}")
                raise WhatsAppProviderNotAvailable(f"Provider '{provider_name}' não disponível: {e}")
            except Exception as e:
                logger.error(f"Erro ao inicializar provider '{provider_name}': {e}", exc_info=True)
                raise WhatsAppProviderNotAvailable(f"Erro ao inicializar provider: {e}")
        
        return self._provider
    
    def send_text(
        self,
        to: str,
        text: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> ProviderResult:
        """
        Envia mensagem de texto
        
        Args:
            to: Número de destino
            text: Texto da mensagem
            metadata: Metadados adicionais (shopper_id, skm_id, correlation_id, etc.)
        
        Returns:
            ProviderResult com resultado da operação
        """
        # Verificar se envio está habilitado
        if not is_whatsapp_send_enabled():
            logger.info(
                f"[WhatsAppGateway] Envio desabilitado (WHATSAPP_SEND_ENABLED=False)",
                extra={'to': to, 'metadata': metadata or {}}
            )
            return ProviderResult(
                provider_name="gateway",
                status="failed",
                error="Envio WhatsApp desabilitado",
                metadata=metadata or {}
            )
        
        # Verificar se shopper está habilitado (se metadata contém shopper_id)
        enabled_shoppers = get_enabled_shoppers()
        if enabled_shoppers and metadata:
            shopper_id = metadata.get('shopper_id')
            if shopper_id and shopper_id not in enabled_shoppers:
                logger.info(
                    f"[WhatsAppGateway] Shopper não habilitado: {shopper_id}",
                    extra={'to': to, 'shopper_id': shopper_id, 'metadata': metadata}
                )
                return ProviderResult(
                    provider_name="gateway",
                    status="failed",
                    error=f"Shopper {shopper_id} não habilitado",
                    metadata=metadata or {}
                )
        
        # Modo shadow: logar sem enviar
        shadow_mode = is_whatsapp_shadow_mode()
        if shadow_mode:
            logger.info(
                f"[WhatsAppGateway] Modo shadow: logaria envio sem enviar",
                extra={
                    'to': to,
                    'text_length': len(text),
                    'text_preview': text[:100] + '...' if len(text) > 100 else text,
                    'metadata': metadata or {}
                }
            )
            return ProviderResult(
                provider_name="gateway",
                status="sent",  # Simula sucesso
                message_id=f"shadow_{id(self)}",
                metadata={
                    'shadow_mode': True,
                    **({} if metadata is None else metadata)
                }
            )
        
        # Enviar via provider
        try:
            provider = self._get_provider()
            
            # Log estruturado (sem dados sensíveis)
            logger.info(
                f"[WhatsAppGateway] Enviando mensagem via {provider.name}",
                extra={
                    'provider': provider.name,
                    'to': to,
                    'text_length': len(text),
                    'shopper_id': metadata.get('shopper_id') if metadata else None,
                    'skm_id': metadata.get('skm_id') if metadata else None,
                    'correlation_id': metadata.get('correlation_id') if metadata else None,
                }
            )
            
            result = provider.send_text(to=to, text=text, metadata=metadata)
            
            # Log resultado
            if result.is_success():
                logger.info(
                    f"[WhatsAppGateway] Mensagem enviada com sucesso",
                    extra={
                        'provider': provider.name,
                        'message_id': result.message_id,
                        'status': result.status,
                    }
                )
            else:
                logger.error(
                    f"[WhatsAppGateway] Erro ao enviar mensagem",
                    extra={
                        'provider': provider.name,
                        'error': result.error,
                        'status': result.status,
                    }
                )
            
            return result
        
        except WhatsAppProviderNotAvailable as e:
            logger.error(f"[WhatsAppGateway] Provider não disponível: {e}")
            return ProviderResult(
                provider_name="gateway",
                status="failed",
                error=str(e),
                metadata=metadata or {}
            )
        except Exception as e:
            logger.error(f"[WhatsAppGateway] Erro inesperado: {e}", exc_info=True)
            return ProviderResult(
                provider_name="gateway",
                status="failed",
                error=f"Erro inesperado: {str(e)}",
                metadata=metadata or {}
            )
    
    def send_media(
        self,
        to: str,
        media_url: str,
        caption: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> ProviderResult:
        """
        Envia mídia
        
        Args:
            to: Número de destino
            media_url: URL da mídia
            caption: Legenda (opcional)
            metadata: Metadados adicionais
        
        Returns:
            ProviderResult com resultado da operação
        """
        # Verificar se envio está habilitado
        if not is_whatsapp_send_enabled():
            logger.info(
                f"[WhatsAppGateway] Envio desabilitado (WHATSAPP_SEND_ENABLED=False)",
                extra={'to': to, 'metadata': metadata or {}}
            )
            return ProviderResult(
                provider_name="gateway",
                status="failed",
                error="Envio WhatsApp desabilitado",
                metadata=metadata or {}
            )
        
        # Verificar se shopper está habilitado
        enabled_shoppers = get_enabled_shoppers()
        if enabled_shoppers and metadata:
            shopper_id = metadata.get('shopper_id')
            if shopper_id and shopper_id not in enabled_shoppers:
                logger.info(
                    f"[WhatsAppGateway] Shopper não habilitado: {shopper_id}",
                    extra={'to': to, 'shopper_id': shopper_id, 'metadata': metadata}
                )
                return ProviderResult(
                    provider_name="gateway",
                    status="failed",
                    error=f"Shopper {shopper_id} não habilitado",
                    metadata=metadata or {}
                )
        
        # Modo shadow: logar sem enviar
        shadow_mode = is_whatsapp_shadow_mode()
        if shadow_mode:
            logger.info(
                f"[WhatsAppGateway] Modo shadow: logaria envio de mídia sem enviar",
                extra={
                    'to': to,
                    'media_url': media_url,
                    'caption': caption,
                    'metadata': metadata or {}
                }
            )
            return ProviderResult(
                provider_name="gateway",
                status="sent",  # Simula sucesso
                message_id=f"shadow_{id(self)}",
                metadata={
                    'shadow_mode': True,
                    **({} if metadata is None else metadata)
                }
            )
        
        # Enviar via provider
        try:
            provider = self._get_provider()
            
            # Log estruturado
            logger.info(
                f"[WhatsAppGateway] Enviando mídia via {provider.name}",
                extra={
                    'provider': provider.name,
                    'to': to,
                    'media_url': media_url,
                    'shopper_id': metadata.get('shopper_id') if metadata else None,
                    'skm_id': metadata.get('skm_id') if metadata else None,
                }
            )
            
            result = provider.send_media(to=to, media_url=media_url, caption=caption, metadata=metadata)
            
            # Log resultado
            if result.is_success():
                logger.info(
                    f"[WhatsAppGateway] Mídia enviada com sucesso",
                    extra={
                        'provider': provider.name,
                        'message_id': result.message_id,
                        'status': result.status,
                    }
                )
            else:
                logger.error(
                    f"[WhatsAppGateway] Erro ao enviar mídia",
                    extra={
                        'provider': provider.name,
                        'error': result.error,
                        'status': result.status,
                    }
                )
            
            return result
        
        except WhatsAppProviderNotAvailable as e:
            logger.error(f"[WhatsAppGateway] Provider não disponível: {e}")
            return ProviderResult(
                provider_name="gateway",
                status="failed",
                error=str(e),
                metadata=metadata or {}
            )
        except Exception as e:
            logger.error(f"[WhatsAppGateway] Erro inesperado: {e}", exc_info=True)
            return ProviderResult(
                provider_name="gateway",
                status="failed",
                error=f"Erro inesperado: {str(e)}",
                metadata=metadata or {}
            )
    
    def healthcheck(self) -> ProviderHealth:
        """
        Verifica saúde do gateway e provider ativo
        
        Returns:
            ProviderHealth com status
        """
        try:
            provider = self._get_provider()
            return provider.healthcheck()
        except Exception as e:
            logger.error(f"[WhatsAppGateway] Erro no healthcheck: {e}", exc_info=True)
            return ProviderHealth(
                provider_name="gateway",
                status="unhealthy",
                message=f"Erro ao verificar saúde: {str(e)}",
                last_check=datetime.now()
            )


# Singleton global
_gateway_instance: Optional[WhatsAppGateway] = None


def get_whatsapp_gateway() -> WhatsAppGateway:
    """
    Obtém instância singleton do gateway
    
    Returns:
        Instância do WhatsAppGateway
    """
    global _gateway_instance
    if _gateway_instance is None:
        _gateway_instance = WhatsAppGateway()
    return _gateway_instance
