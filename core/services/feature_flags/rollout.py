"""
Rollout Manager
===============

Gerenciador de rollout gradual com suporte a:
- Allowlist (lista explícita de shopper_ids)
- Denylist (lista de shopper_ids bloqueados)
- Percent rollout (percentual global com hash determinístico)
- Shadow mode (executa sem interferir)
- Dual-run (executa legado + novo para comparação)
"""

import hashlib
import logging
from typing import Optional, Dict, Any
from .settings import FeatureFlagConfig, get_feature_flag
from .storage import get_flag_storage

logger = logging.getLogger(__name__)


class RolloutManager:
    """
    Gerenciador de rollout gradual
    """
    
    def __init__(self):
        self.storage = get_flag_storage()
        self._cache: Dict[str, FeatureFlagConfig] = {}
    
    def _get_config(self, flag_name: str) -> Optional[FeatureFlagConfig]:
        """Obtém configuração de flag (com cache)"""
        if flag_name not in self._cache:
            config = self.storage.get_flag(flag_name)
            if config:
                self._cache[flag_name] = config
        return self._cache.get(flag_name)
    
    def _clear_cache(self, flag_name: Optional[str] = None):
        """Limpa cache (útil após atualizações)"""
        if flag_name:
            self._cache.pop(flag_name, None)
        else:
            self._cache.clear()
    
    def is_enabled(
        self,
        flag_name: str,
        shopper_id: Optional[str] = None,
        skm_id: Optional[str] = None,
        default: bool = False
    ) -> bool:
        """
        Verifica se feature flag está habilitada
        
        Precedência:
        1. Denylist (se shopper_id está na denylist -> False)
        2. Allowlist (se shopper_id está na allowlist -> True)
        3. Percent rollout (hash determinístico do shopper_id)
        4. Global enabled/disabled
        5. Default
        
        Args:
            flag_name: Nome da flag
            shopper_id: ID do shopper (opcional, para rollout por shopper)
            skm_id: ID do SKM (opcional, para rollout por SKM)
            default: Valor padrão se flag não encontrada
            
        Returns:
            True se habilitada, False caso contrário
        """
        config = self._get_config(flag_name)
        if not config:
            return default
        
        # Se globalmente desabilitado, retornar False
        if not config.enabled:
            return False
        
        # Se não há shopper_id, retornar enabled global
        if not shopper_id:
            return config.enabled
        
        # 1. Verificar denylist (maior precedência)
        if config.denylist and shopper_id in config.denylist:
            logger.debug(f"Flag {flag_name} desabilitada para shopper {shopper_id} (denylist)")
            return False
        
        # 2. Verificar allowlist
        if config.allowlist:
            if shopper_id in config.allowlist:
                logger.debug(f"Flag {flag_name} habilitada para shopper {shopper_id} (allowlist)")
                return True
            else:
                # Se há allowlist mas shopper não está nela, desabilitar
                logger.debug(f"Flag {flag_name} desabilitada para shopper {shopper_id} (não está na allowlist)")
                return False
        
        # 3. Verificar percent rollout
        if config.percent_rollout > 0:
            enabled = self._check_percent_rollout(shopper_id, config.percent_rollout)
            if enabled:
                logger.debug(f"Flag {flag_name} habilitada para shopper {shopper_id} (percent rollout {config.percent_rollout}%)")
            else:
                logger.debug(f"Flag {flag_name} desabilitada para shopper {shopper_id} (percent rollout {config.percent_rollout}%)")
            return enabled
        
        # 4. Global enabled
        return config.enabled
    
    def _check_percent_rollout(self, shopper_id: str, percent: int) -> bool:
        """
        Verifica se shopper_id está no percentual de rollout
        
        Usa hash determinístico para garantir que o mesmo shopper_id
        sempre recebe o mesmo resultado.
        
        Args:
            shopper_id: ID do shopper
            percent: Percentual (0-100)
            
        Returns:
            True se shopper está no percentual
        """
        if percent <= 0:
            return False
        if percent >= 100:
            return True
        
        # Hash determinístico do shopper_id
        hash_obj = hashlib.md5(shopper_id.encode())
        hash_int = int(hash_obj.hexdigest(), 16)
        
        # Módulo 100 para obter valor 0-99
        bucket = hash_int % 100
        
        # Se bucket < percent, está habilitado
        return bucket < percent
    
    def is_shadow_mode(self, flag_name: str) -> bool:
        """
        Verifica se flag está em shadow mode
        
        Args:
            flag_name: Nome da flag
            
        Returns:
            True se shadow mode ativo
        """
        config = self._get_config(flag_name)
        if not config:
            return False
        return config.shadow_mode
    
    def is_dual_run(self, flag_name: str) -> bool:
        """
        Verifica se dual-run está habilitado
        
        Args:
            flag_name: Nome da flag
            
        Returns:
            True se dual-run ativo
        """
        # Dual-run é controlado por flag específica
        dual_run_flag = f'{flag_name}_DUAL_RUN'
        return self.is_enabled(dual_run_flag, default=False)
    
    def get_metadata(self, flag_name: str, key: Optional[str] = None) -> Any:
        """
        Obtém metadata da flag
        
        Args:
            flag_name: Nome da flag
            key: Chave específica (opcional)
            
        Returns:
            Metadata completo ou valor da chave
        """
        config = self._get_config(flag_name)
        if not config:
            return None if key else {}
        
        if key:
            return config.metadata.get(key)
        return config.metadata


# Singleton
_rollout_instance: Optional[RolloutManager] = None


def get_rollout_manager() -> RolloutManager:
    """Obtém instância singleton do rollout manager"""
    global _rollout_instance
    if _rollout_instance is None:
        _rollout_instance = RolloutManager()
    return _rollout_instance


def is_enabled(
    flag_name: str,
    shopper_id: Optional[str] = None,
    skm_id: Optional[str] = None,
    default: bool = False
) -> bool:
    """
    Função canônica para verificar se flag está habilitada
    
    Args:
        flag_name: Nome da flag
        shopper_id: ID do shopper (opcional)
        skm_id: ID do SKM (opcional)
        default: Valor padrão
        
    Returns:
        True se habilitada
    """
    manager = get_rollout_manager()
    return manager.is_enabled(flag_name, shopper_id, skm_id, default)
