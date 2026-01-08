"""
Feature Flags Observability
===========================

Métricas e logs estruturados para observabilidade do rollout.
"""

import logging
import time
from typing import Optional, Dict, Any
from django.utils import timezone

logger = logging.getLogger(__name__)


class FeatureFlagMetrics:
    """
    Métricas de feature flags
    """
    
    @staticmethod
    def log_flag_check(
        flag_name: str,
        enabled: bool,
        shopper_id: Optional[str] = None,
        skm_id: Optional[str] = None,
        reason: Optional[str] = None,
        correlation_id: Optional[str] = None
    ):
        """
        Loga verificação de flag
        
        Args:
            flag_name: Nome da flag
            enabled: Se está habilitada
            shopper_id: ID do shopper
            skm_id: ID do SKM
            reason: Razão da decisão (allowlist, denylist, percent, etc.)
            correlation_id: ID de correlação
        """
        log_data = {
            'event': 'feature_flag_check',
            'flag_name': flag_name,
            'enabled': enabled,
            'reason': reason or 'default',
            'timestamp': timezone.now().isoformat(),
        }
        
        if shopper_id:
            log_data['shopper_id'] = shopper_id
        if skm_id:
            log_data['skm_id'] = skm_id
        if correlation_id:
            log_data['correlation_id'] = correlation_id
        
        logger.info(f"[FEATURE_FLAG] {flag_name}={enabled} (reason: {reason})", extra=log_data)
    
    @staticmethod
    def log_canonical_event_published(
        event_id: str,
        shopper_id: Optional[str] = None,
        success: bool = True,
        error: Optional[str] = None,
        latency_ms: Optional[float] = None,
        correlation_id: Optional[str] = None
    ):
        """
        Loga publicação de evento canônico
        
        Args:
            event_id: ID do evento
            shopper_id: ID do shopper
            success: Se foi bem-sucedido
            error: Mensagem de erro (se houver)
            latency_ms: Latência em milissegundos
            correlation_id: ID de correlação
        """
        log_data = {
            'event': 'canonical_event_published',
            'event_id': event_id,
            'success': success,
            'timestamp': timezone.now().isoformat(),
        }
        
        if shopper_id:
            log_data['shopper_id'] = shopper_id
        if error:
            log_data['error'] = error
        if latency_ms is not None:
            log_data['latency_ms'] = latency_ms
        if correlation_id:
            log_data['correlation_id'] = correlation_id
        
        if success:
            logger.info(f"[CANONICAL_EVENT] Published: {event_id}", extra=log_data)
        else:
            logger.error(f"[CANONICAL_EVENT] Failed: {event_id} - {error}", extra=log_data)
    
    @staticmethod
    def log_routing_assignment(
        shopper_id: str,
        skm_id: Optional[str],
        thread_key: str,
        success: bool = True,
        error: Optional[str] = None,
        latency_ms: Optional[float] = None,
        correlation_id: Optional[str] = None
    ):
        """
        Loga atribuição de roteamento
        
        Args:
            shopper_id: ID do shopper
            skm_id: ID do SKM atribuído
            thread_key: Chave do thread
            success: Se foi bem-sucedido
            error: Mensagem de erro (se houver)
            latency_ms: Latência em milissegundos
            correlation_id: ID de correlação
        """
        log_data = {
            'event': 'routing_assignment',
            'shopper_id': shopper_id,
            'skm_id': skm_id,
            'thread_key': thread_key,
            'success': success,
            'timestamp': timezone.now().isoformat(),
        }
        
        if error:
            log_data['error'] = error
        if latency_ms is not None:
            log_data['latency_ms'] = latency_ms
        if correlation_id:
            log_data['correlation_id'] = correlation_id
        
        if success:
            logger.info(f"[ROUTING] Assigned: shopper={shopper_id}, skm={skm_id}", extra=log_data)
        else:
            logger.error(f"[ROUTING] Failed: shopper={shopper_id} - {error}", extra=log_data)
    
    @staticmethod
    def log_dual_run_divergence(
        shopper_id: str,
        thread_key: str,
        legacy_result: Dict[str, Any],
        canonical_result: Dict[str, Any],
        differences: list,
        correlation_id: Optional[str] = None
    ):
        """
        Loga divergências entre legado e canônico (dual-run)
        
        Args:
            shopper_id: ID do shopper
            thread_key: Chave do thread
            legacy_result: Resultado do pipeline legado
            canonical_result: Resultado do pipeline canônico
            differences: Lista de diferenças encontradas
            correlation_id: ID de correlação
        """
        log_data = {
            'event': 'dual_run_divergence',
            'shopper_id': shopper_id,
            'thread_key': thread_key,
            'differences': differences,
            'legacy_result': legacy_result,
            'canonical_result': canonical_result,
            'timestamp': timezone.now().isoformat(),
        }
        
        if correlation_id:
            log_data['correlation_id'] = correlation_id
        
        logger.warning(
            f"[DUAL_RUN] Divergence detected: shopper={shopper_id}, differences={len(differences)}",
            extra=log_data
        )


class TimingContext:
    """
    Context manager para medir latência
    """
    
    def __init__(self, operation_name: str):
        self.operation_name = operation_name
        self.start_time = None
        self.latency_ms = None
    
    def __enter__(self):
        self.start_time = time.time()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.start_time:
            self.latency_ms = (time.time() - self.start_time) * 1000
        return False
    
    def get_latency_ms(self) -> Optional[float]:
        """Retorna latência em milissegundos"""
        return self.latency_ms
