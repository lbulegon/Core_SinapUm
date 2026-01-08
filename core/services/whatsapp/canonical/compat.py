"""
Compat Layer - WhatsApp Canonical Events v1.0
==============================================

Camada de compatibilidade para webhooks existentes.
Permite que webhooks atuais continuem funcionando, mas opcionalmente
gerem eventos canônicos em shadow mode (feature flag).

INTEGRAÇÃO COM ROLLOUT MANAGER:
- Usa feature flags para controle gradual
- Suporta shadow mode, dual-run e rollout por shopper_id
"""
import logging
from typing import Dict, Any, Optional, Callable
from django.conf import settings

from .normalizer import get_event_normalizer
from .publisher import get_event_publisher
from .schemas import EventEnvelope

# Importar rollout manager
try:
    from core.services.feature_flags.rollout import get_rollout_manager
    from core.services.feature_flags.observability import (
        FeatureFlagMetrics,
        TimingContext
    )
    ROLLOUT_AVAILABLE = True
except ImportError:
    ROLLOUT_AVAILABLE = False
    logger = logging.getLogger(__name__)
    logger.warning("Rollout manager não disponível, usando configuração direta")

logger = logging.getLogger(__name__)


class WebhookCompatLayer:
    """
    Camada de compatibilidade para webhooks existentes
    
    Permite que webhooks atuais continuem funcionando normalmente,
    mas opcionalmente gerem eventos canônicos em shadow mode.
    
    INTEGRAÇÃO COM ROLLOUT:
    - Verifica feature flags via rollout manager
    - Suporta rollout por shopper_id (allowlist, denylist, percent)
    - Suporta dual-run para comparação legado vs novo
    """
    
    def __init__(self):
        self.normalizer = get_event_normalizer()
        self.publisher = get_event_publisher()
        
        # Rollout manager (se disponível)
        if ROLLOUT_AVAILABLE:
            self.rollout_manager = get_rollout_manager()
            self.metrics = FeatureFlagMetrics()
        else:
            self.rollout_manager = None
            self.metrics = None
            # Fallback para configuração direta
            self.enabled = getattr(settings, 'WHATSAPP_CANONICAL_EVENTS_ENABLED', False)
            self.shadow_mode = getattr(settings, 'WHATSAPP_CANONICAL_SHADOW_MODE', False)
    
    def _is_enabled_for_shopper(self, shopper_id: Optional[str] = None) -> bool:
        """
        Verifica se eventos canônicos estão habilitados para shopper
        
        Args:
            shopper_id: ID do shopper (opcional)
            
        Returns:
            True se habilitado
        """
        if self.rollout_manager:
            return self.rollout_manager.is_enabled(
                'WHATSAPP_CANONICAL_EVENTS_ENABLED',
                shopper_id=shopper_id,
                default=False
            )
        return self.enabled
    
    def _is_shadow_mode(self) -> bool:
        """Verifica se está em shadow mode"""
        if self.rollout_manager:
            return self.rollout_manager.is_shadow_mode('WHATSAPP_CANONICAL_EVENTS_ENABLED')
        return self.shadow_mode
    
    def _is_dual_run(self) -> bool:
        """Verifica se dual-run está habilitado"""
        if self.rollout_manager:
            return self.rollout_manager.is_dual_run('WHATSAPP_CANONICAL_EVENTS_ENABLED')
        return False
    
    def wrap_webhook_handler(
        self,
        original_handler: Callable,
        provider: str,
        instance_key: Optional[str] = None
    ) -> Callable:
        """
        Wraps um handler de webhook existente para gerar eventos canônicos
        
        Args:
            original_handler: Função original do webhook handler
            provider: Nome do provider (evolution, cloud, baileys, etc.)
            instance_key: Chave da instância (opcional)
        
        Returns:
            Função wrapper que chama original_handler e gera evento canônico
        """
        def wrapper(request, *args, **kwargs):
            # Extrair shopper_id do payload (se disponível)
            shopper_id = self._extract_shopper_id(request)
            
            # Verificar se está habilitado para este shopper
            enabled = self._is_enabled_for_shopper(shopper_id)
            shadow_mode = self._is_shadow_mode()
            dual_run = self._is_dual_run()
            
            # Logar verificação de flag
            if self.metrics:
                reason = self._get_enable_reason(shopper_id)
                self.metrics.log_flag_check(
                    'WHATSAPP_CANONICAL_EVENTS_ENABLED',
                    enabled,
                    shopper_id=shopper_id,
                    reason=reason
                )
            
            # Chamar handler original primeiro (não quebra comportamento existente)
            response = original_handler(request, *args, **kwargs)
            
            # Se eventos canônicos estão habilitados, gerar evento
            if enabled:
                try:
                    # Extrair payload do request
                    raw_payload = self._extract_payload(request)
                    
                    if raw_payload:
                        # Normalizar para evento canônico
                        envelope = self.normalizer.normalize(
                            provider=provider,
                            raw_payload=raw_payload,
                            instance_key=instance_key
                        )
                        
                        if envelope:
                            # Medir latência
                            with TimingContext('canonical_publish') as timing:
                                # Publicar (em shadow mode, apenas loga)
                                if shadow_mode:
                                    logger.info(
                                        f"[SHADOW MODE] Evento canônico gerado (não persistido): "
                                        f"{envelope.event_type.value} from {envelope.from_number}"
                                    )
                                    if self.metrics:
                                        self.metrics.log_canonical_event_published(
                                            envelope.event_id,
                                            shopper_id=shopper_id,
                                            success=True,
                                            latency_ms=timing.get_latency_ms()
                                        )
                                else:
                                    # Publicar normalmente
                                    try:
                                        self.publisher.publish(envelope, emit_signal=True)
                                        logger.debug(
                                            f"Evento canônico gerado via compat layer: "
                                            f"{envelope.event_type.value}"
                                        )
                                        if self.metrics:
                                            self.metrics.log_canonical_event_published(
                                                envelope.event_id,
                                                shopper_id=shopper_id,
                                                success=True,
                                                latency_ms=timing.get_latency_ms()
                                            )
                                    except Exception as e:
                                        if self.metrics:
                                            self.metrics.log_canonical_event_published(
                                                envelope.event_id,
                                                shopper_id=shopper_id,
                                                success=False,
                                                error=str(e),
                                                latency_ms=timing.get_latency_ms()
                                            )
                                        raise
                
                except Exception as e:
                    # Não quebrar o fluxo original se houver erro
                    logger.error(
                        f"Erro ao gerar evento canônico via compat layer: {e}",
                        exc_info=True
                    )
            
            # Retornar resposta original (não altera comportamento)
            return response
        
        return wrapper
    
    def process_webhook_payload(
        self,
        provider: str,
        raw_payload: Dict[str, Any],
        instance_key: Optional[str] = None,
        persist: bool = True,
        shopper_id: Optional[str] = None
    ) -> Optional[EventEnvelope]:
        """
        Processa payload de webhook e gera evento canônico
        
        Args:
            provider: Nome do provider
            raw_payload: Payload bruto do webhook
            instance_key: Chave da instância
            persist: Se True, persiste no EventLog (default: True)
            shopper_id: ID do shopper (opcional, para rollout)
        
        Returns:
            EventEnvelope gerado ou None
        """
        # Verificar se está habilitado para este shopper
        enabled = self._is_enabled_for_shopper(shopper_id)
        if not enabled:
            return None
        
        shadow_mode = self._is_shadow_mode()
        
        try:
            # Normalizar
            envelope = self.normalizer.normalize(
                provider=provider,
                raw_payload=raw_payload,
                instance_key=instance_key
            )
            
            if envelope:
                # Medir latência
                with TimingContext('canonical_publish') as timing:
                    # Publicar se não estiver em shadow mode
                    if not shadow_mode and persist:
                        try:
                            self.publisher.publish(envelope, emit_signal=True)
                            if self.metrics:
                                self.metrics.log_canonical_event_published(
                                    envelope.event_id,
                                    shopper_id=shopper_id,
                                    success=True,
                                    latency_ms=timing.get_latency_ms()
                                )
                        except Exception as e:
                            if self.metrics:
                                self.metrics.log_canonical_event_published(
                                    envelope.event_id,
                                    shopper_id=shopper_id,
                                    success=False,
                                    error=str(e),
                                    latency_ms=timing.get_latency_ms()
                                )
                            raise
                    elif shadow_mode:
                        logger.info(
                            f"[SHADOW MODE] Evento canônico normalizado (não persistido): "
                            f"{envelope.event_type.value}"
                        )
                        if self.metrics:
                            self.metrics.log_canonical_event_published(
                                envelope.event_id,
                                shopper_id=shopper_id,
                                success=True,
                                latency_ms=timing.get_latency_ms()
                            )
            
            return envelope
        
        except Exception as e:
            logger.error(f"Erro ao processar webhook payload: {e}", exc_info=True)
            return None
    
    def _extract_payload(self, request) -> Optional[Dict[str, Any]]:
        """Extrai payload do request"""
        try:
            if hasattr(request, 'data'):
                # DRF request
                return request.data
            elif hasattr(request, 'body'):
                # Django request com JSON
                import json
                return json.loads(request.body)
            elif hasattr(request, 'POST'):
                # Django request com form data
                return dict(request.POST)
            return None
        except Exception as e:
            logger.error(f"Erro ao extrair payload: {e}")
            return None
    
    def _extract_shopper_id(self, request) -> Optional[str]:
        """
        Extrai shopper_id do request/payload
        
        Args:
            request: Request object
            
        Returns:
            shopper_id ou None
        """
        try:
            payload = self._extract_payload(request)
            if payload:
                # Tentar diferentes caminhos comuns
                if isinstance(payload, dict):
                    # Direto no payload
                    if 'shopper_id' in payload:
                        return str(payload['shopper_id'])
                    # Em data
                    if 'data' in payload and isinstance(payload['data'], dict):
                        if 'shopper_id' in payload['data']:
                            return str(payload['data']['shopper_id'])
                    # Em metadata
                    if 'metadata' in payload and isinstance(payload['metadata'], dict):
                        if 'shopper_id' in payload['metadata']:
                            return str(payload['metadata']['shopper_id'])
            return None
        except Exception as e:
            logger.debug(f"Erro ao extrair shopper_id: {e}")
            return None
    
    def _get_enable_reason(self, shopper_id: Optional[str]) -> str:
        """
        Obtém razão pela qual flag está habilitada/desabilitada
        
        Args:
            shopper_id: ID do shopper
            
        Returns:
            Razão (allowlist, denylist, percent, global, default)
        """
        if not self.rollout_manager or not shopper_id:
            return 'global'
        
        try:
            config = self.rollout_manager._get_config('WHATSAPP_CANONICAL_EVENTS_ENABLED')
            if not config:
                return 'default'
            
            if config.denylist and shopper_id in config.denylist:
                return 'denylist'
            if config.allowlist and shopper_id in config.allowlist:
                return 'allowlist'
            if config.percent_rollout > 0:
                return f'percent_{config.percent_rollout}'
            if config.enabled:
                return 'global'
            return 'default'
        except Exception:
            return 'default'


# Singleton
_compat_layer_instance: Optional[WebhookCompatLayer] = None


def get_webhook_compat_layer() -> WebhookCompatLayer:
    """Obtém instância singleton da camada de compatibilidade"""
    global _compat_layer_instance
    if _compat_layer_instance is None:
        _compat_layer_instance = WebhookCompatLayer()
    return _compat_layer_instance
