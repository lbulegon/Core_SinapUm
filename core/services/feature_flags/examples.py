"""
Exemplos de Uso - Feature Flags
================================

Exemplos práticos de como usar o sistema de feature flags.
"""

from core.services.feature_flags.rollout import is_enabled, get_rollout_manager
from core.services.feature_flags.observability import FeatureFlagMetrics


# ============================================================================
# Exemplo 1: Verificação Básica
# ============================================================================

def exemplo_verificacao_basica():
    """Verifica se flag está habilitada"""
    
    # Verificação global
    if is_enabled('WHATSAPP_CANONICAL_EVENTS_ENABLED'):
        print("Eventos canônicos habilitados globalmente")
    
    # Verificação por shopper
    shopper_id = "shopper_123"
    if is_enabled('WHATSAPP_CANONICAL_EVENTS_ENABLED', shopper_id=shopper_id):
        print(f"Eventos canônicos habilitados para {shopper_id}")


# ============================================================================
# Exemplo 2: Uso em Webhook Handler
# ============================================================================

def exemplo_webhook_handler(request, shopper_id: str):
    """Exemplo de uso em webhook handler"""
    
    from core.services.feature_flags.rollout import get_rollout_manager
    from core.services.feature_flags.observability import FeatureFlagMetrics, TimingContext
    
    manager = get_rollout_manager()
    metrics = FeatureFlagMetrics()
    
    # Verificar se está habilitado
    enabled = manager.is_enabled(
        'WHATSAPP_CANONICAL_EVENTS_ENABLED',
        shopper_id=shopper_id
    )
    
    if not enabled:
        # Fluxo legado (não quebra comportamento existente)
        return process_legacy(request)
    
    # Novo fluxo
    shadow_mode = manager.is_shadow_mode('WHATSAPP_CANONICAL_EVENTS_ENABLED')
    dual_run = manager.is_dual_run('WHATSAPP_CANONICAL_EVENTS_ENABLED')
    
    # Logar verificação
    reason = manager._get_enable_reason(shopper_id)
    metrics.log_flag_check(
        'WHATSAPP_CANONICAL_EVENTS_ENABLED',
        enabled,
        shopper_id=shopper_id,
        reason=reason
    )
    
    # Processar novo fluxo
    with TimingContext('canonical_process') as timing:
        result = process_canonical(request, shopper_id)
        
        # Logar métricas
        metrics.log_canonical_event_published(
            result.get('event_id'),
            shopper_id=shopper_id,
            success=result.get('success', False),
            latency_ms=timing.get_latency_ms()
        )
    
    # Dual-run: também executar legado para comparação
    if dual_run:
        legacy_result = process_legacy(request)
        compare_results(legacy_result, result, shopper_id)
    
    return result


# ============================================================================
# Exemplo 3: Configuração via DB
# ============================================================================

def exemplo_configurar_via_db():
    """Exemplo de como configurar flags via DB"""
    
    from core.services.feature_flags.models import FeatureFlagConfig
    from core.services.feature_flags.storage import get_flag_storage
    
    storage = get_flag_storage()
    
    # Criar/atualizar flag
    config = FeatureFlagConfig(
        name='WHATSAPP_CANONICAL_EVENTS_ENABLED',
        enabled=True,
        shadow_mode=True,
        allowlist=['shopper_001', 'shopper_002'],
        denylist=[],
        percent_rollout=0,
        metadata={'phase': 'canary'}
    )
    
    storage.set_flag('WHATSAPP_CANONICAL_EVENTS_ENABLED', config)
    
    # Limpar cache
    manager = get_rollout_manager()
    manager._clear_cache('WHATSAPP_CANONICAL_EVENTS_ENABLED')


# ============================================================================
# Exemplo 4: Rollout Percentual
# ============================================================================

def exemplo_rollout_percentual():
    """Exemplo de rollout percentual gradual"""
    
    from core.services.feature_flags.storage import get_flag_storage
    
    storage = get_flag_storage()
    manager = get_rollout_manager()
    
    # Fase 1: 5%
    config = FeatureFlagConfig(
        name='WHATSAPP_CANONICAL_EVENTS_ENABLED',
        enabled=True,
        shadow_mode=True,
        allowlist=[],
        denylist=[],
        percent_rollout=5
    )
    storage.set_flag('WHATSAPP_CANONICAL_EVENTS_ENABLED', config)
    manager._clear_cache('WHATSAPP_CANONICAL_EVENTS_ENABLED')
    
    # Após 24h, aumentar para 10%
    config.percent_rollout = 10
    storage.set_flag('WHATSAPP_CANONICAL_EVENTS_ENABLED', config)
    manager._clear_cache('WHATSAPP_CANONICAL_EVENTS_ENABLED')
    
    # E assim por diante: 25%, 50%, 100%


# ============================================================================
# Exemplo 5: Rollback
# ============================================================================

def exemplo_rollback():
    """Exemplo de rollback rápido"""
    
    from core.services.feature_flags.storage import get_flag_storage
    
    storage = get_flag_storage()
    manager = get_rollout_manager()
    
    # Rollback global
    config = storage.get_flag('WHATSAPP_CANONICAL_EVENTS_ENABLED')
    if config:
        config.enabled = False
        storage.set_flag('WHATSAPP_CANONICAL_EVENTS_ENABLED', config)
        manager._clear_cache('WHATSAPP_CANONICAL_EVENTS_ENABLED')
    
    # Rollback por shopper (adicionar à denylist)
    config = storage.get_flag('WHATSAPP_CANONICAL_EVENTS_ENABLED')
    if config:
        if 'shopper_problematico' not in config.denylist:
            config.denylist.append('shopper_problematico')
            storage.set_flag('WHATSAPP_CANONICAL_EVENTS_ENABLED', config)
            manager._clear_cache('WHATSAPP_CANONICAL_EVENTS_ENABLED')


# ============================================================================
# Funções auxiliares (exemplos)
# ============================================================================

def process_legacy(request):
    """Processa via fluxo legado"""
    # Implementação legada
    return {'success': True, 'method': 'legacy'}


def process_canonical(request, shopper_id: str):
    """Processa via fluxo canônico"""
    # Implementação nova
    return {'success': True, 'method': 'canonical', 'event_id': 'evt_123'}


def compare_results(legacy_result, canonical_result, shopper_id: str):
    """Compara resultados legado vs canônico"""
    from core.services.feature_flags.observability import FeatureFlagMetrics
    
    metrics = FeatureFlagMetrics()
    
    differences = []
    if legacy_result.get('thread_key') != canonical_result.get('thread_key'):
        differences.append('thread_key')
    if legacy_result.get('conversation_id') != canonical_result.get('conversation_id'):
        differences.append('conversation_id')
    
    if differences:
        metrics.log_dual_run_divergence(
            shopper_id,
            canonical_result.get('thread_key', 'unknown'),
            legacy_result,
            canonical_result,
            differences
        )
