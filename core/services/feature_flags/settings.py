"""
Feature Flags Settings
======================

Definição de feature flags e configurações padrão.
"""

from typing import Dict, Any, Optional
from django.conf import settings
import os

# Feature Flags Definidas
FEATURE_FLAGS = {
    # WhatsApp Canonical Events
    'WHATSAPP_CANONICAL_EVENTS_ENABLED': {
        'default': False,
        'description': 'Habilita eventos canônicos WhatsApp',
        'type': 'bool',
    },
    'WHATSAPP_CANONICAL_SHADOW_MODE': {
        'default': True,
        'description': 'Modo shadow para eventos canônicos (não interfere no fluxo)',
        'type': 'bool',
    },
    
    # WhatsApp Routing
    'WHATSAPP_ROUTING_ENABLED': {
        'default': False,
        'description': 'Habilita roteamento de mensagens WhatsApp',
        'type': 'bool',
    },
    
    # WhatsApp Gateway
    'WHATSAPP_GATEWAY_ENABLED': {
        'default': False,
        'description': 'Habilita novo gateway WhatsApp',
        'type': 'bool',
    },
    
    # Dual Run (comparação legado vs novo)
    'WHATSAPP_DUAL_RUN': {
        'default': False,
        'description': 'Executa legado e novo pipeline em paralelo para comparação',
        'type': 'bool',
    },
    
    # Delivery Area
    'DELIVERY_AREA_ENABLED': {
        'default': False,
        'description': 'Habilita funcionalidades de área de entrega',
        'type': 'bool',
    },
    
    # SKM Score Events
    'SKM_SCORE_EVENTS_ENABLED': {
        'default': False,
        'description': 'Habilita emissão de eventos para SKM Score',
        'type': 'bool',
    },
}


class FeatureFlagConfig:
    """
    Configuração de uma feature flag
    """
    
    def __init__(
        self,
        name: str,
        enabled: bool = False,
        shadow_mode: bool = False,
        allowlist: Optional[list] = None,
        denylist: Optional[list] = None,
        percent_rollout: int = 0,
        metadata: Optional[Dict[str, Any]] = None
    ):
        self.name = name
        self.enabled = enabled
        self.shadow_mode = shadow_mode
        self.allowlist = allowlist or []
        self.denylist = denylist or []
        self.percent_rollout = max(0, min(100, percent_rollout))  # Clamp 0-100
        self.metadata = metadata or {}
    
    def to_dict(self) -> Dict[str, Any]:
        """Converte para dicionário"""
        return {
            'name': self.name,
            'enabled': self.enabled,
            'shadow_mode': self.shadow_mode,
            'allowlist': self.allowlist,
            'denylist': self.denylist,
            'percent_rollout': self.percent_rollout,
            'metadata': self.metadata,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'FeatureFlagConfig':
        """Cria a partir de dicionário"""
        return cls(
            name=data['name'],
            enabled=data.get('enabled', False),
            shadow_mode=data.get('shadow_mode', False),
            allowlist=data.get('allowlist', []),
            denylist=data.get('denylist', []),
            percent_rollout=data.get('percent_rollout', 0),
            metadata=data.get('metadata', {}),
        )


def get_feature_flag(flag_name: str) -> Optional[FeatureFlagConfig]:
    """
    Obtém configuração de feature flag
    
    Args:
        flag_name: Nome da flag
        
    Returns:
        FeatureFlagConfig ou None se não encontrada
    """
    # Primeiro, tentar obter do storage (DB)
    try:
        from .storage import get_flag_storage
        storage = get_flag_storage()
        config = storage.get_flag(flag_name)
        if config:
            return config
    except Exception:
        pass  # Fallback para env vars
    
    # Fallback: ler de environment variables
    flag_def = FEATURE_FLAGS.get(flag_name)
    if not flag_def:
        return None
    
    # Ler valores de env vars
    enabled = os.environ.get(flag_name, str(flag_def['default'])).lower() in ('true', '1', 'yes')
    
    # Ler allowlist/denylist de env vars (formato: shopper_id1,shopper_id2)
    allowlist_str = os.environ.get(f'{flag_name}_ALLOWLIST', '')
    allowlist = [s.strip() for s in allowlist_str.split(',') if s.strip()] if allowlist_str else []
    
    denylist_str = os.environ.get(f'{flag_name}_DENYLIST', '')
    denylist = [s.strip() for s in denylist_str.split(',') if s.strip()] if denylist_str else []
    
    # Ler percent rollout
    percent_rollout = int(os.environ.get(f'{flag_name}_PERCENT', '0'))
    
    # Ler shadow mode
    shadow_mode = os.environ.get(f'{flag_name}_SHADOW_MODE', 'False').lower() in ('true', '1', 'yes')
    
    return FeatureFlagConfig(
        name=flag_name,
        enabled=enabled,
        shadow_mode=shadow_mode,
        allowlist=allowlist,
        denylist=denylist,
        percent_rollout=percent_rollout,
    )
