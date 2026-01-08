"""
Feature Flags Storage
=====================

Armazenamento de feature flags com suporte a DB e fallback para env vars.
"""

import logging
from typing import Optional, Dict, Any
from django.conf import settings
from .settings import FeatureFlagConfig, get_feature_flag

logger = logging.getLogger(__name__)


class FlagStorage:
    """
    Armazenamento de feature flags
    
    Suporta:
    - DB (FeatureFlagConfig model) - se disponível
    - Env vars (fallback)
    """
    
    def __init__(self):
        self._use_db = None  # Lazy evaluation
        self._db_checked = False
    
    def _check_db_available(self) -> bool:
        """Verifica se model FeatureFlagConfig está disponível (lazy)"""
        if self._db_checked:
            return self._use_db is True
        
        self._db_checked = True
        try:
            # Usar import local dentro de try-except para evitar recursão
            # Se houver recursão, não usar DB
            import sys
            recursion_limit = sys.getrecursionlimit()
            sys.setrecursionlimit(100)  # Reduzir temporariamente para detectar recursão
            
            try:
                from .models import FeatureFlagConfig as FlagModel
                self._use_db = True
                return True
            except RecursionError:
                # Recursão detectada - não usar DB
                logger.warning("Recursão detectada ao importar FeatureFlagConfig, usando apenas env vars")
                self._use_db = False
                return False
            finally:
                sys.setrecursionlimit(recursion_limit)
        except (ImportError, Exception) as e:
            # Se import falhou por qualquer motivo, usar apenas env vars
            logger.debug(f"DB não disponível para feature flags: {e}")
            self._use_db = False
            return False
    
    def get_flag(self, flag_name: str) -> Optional[FeatureFlagConfig]:
        """
        Obtém configuração de flag
        
        Args:
            flag_name: Nome da flag
            
        Returns:
            FeatureFlagConfig ou None
        """
        # Tentar DB primeiro
        if self._check_db_available():
            try:
                from .models import FeatureFlagConfig as FlagModel
                try:
                    db_flag = FlagModel.objects.get(name=flag_name, active=True)
                    return FeatureFlagConfig(
                        name=db_flag.name,
                        enabled=db_flag.enabled,
                        shadow_mode=db_flag.shadow_mode,
                        allowlist=db_flag.allowlist or [],
                        denylist=db_flag.denylist or [],
                        percent_rollout=db_flag.percent_rollout or 0,
                        metadata=db_flag.metadata or {},
                    )
                except FlagModel.DoesNotExist:
                    pass  # Fallback para env vars
                except RecursionError:
                    # Se houver recursão, desabilitar DB e usar env vars
                    logger.warning("Recursão ao acessar DB, desabilitando DB para esta sessão")
                    self._use_db = False
            except RecursionError as e:
                logger.warning(f"Recursão detectada ao acessar DB: {e}, usando fallback env vars")
                self._use_db = False
            except Exception as e:
                logger.warning(f"Erro ao ler flag do DB: {e}, usando fallback env vars")
        
        # Fallback: env vars
        return get_feature_flag(flag_name)
    
    def set_flag(self, flag_name: str, config: FeatureFlagConfig) -> bool:
        """
        Salva configuração de flag (apenas se DB disponível)
        
        Args:
            flag_name: Nome da flag
            config: Configuração
            
        Returns:
            True se salvo, False se apenas env vars disponível
        """
        if not self._check_db_available():
            logger.warning(f"DB não disponível, flag {flag_name} não pode ser salva. Use env vars.")
            return False
        
        try:
            from .models import FeatureFlagConfig as FlagModel
            FlagModel.objects.update_or_create(
                name=flag_name,
                defaults={
                    'enabled': config.enabled,
                    'shadow_mode': config.shadow_mode,
                    'allowlist': config.allowlist,
                    'denylist': config.denylist,
                    'percent_rollout': config.percent_rollout,
                    'metadata': config.metadata,
                    'active': True,
                }
            )
            return True
        except Exception as e:
            logger.error(f"Erro ao salvar flag no DB: {e}")
            return False
    
    def list_flags(self) -> Dict[str, FeatureFlagConfig]:
        """
        Lista todas as flags
        
        Returns:
            Dict com nome -> FeatureFlagConfig
        """
        flags = {}
        
        # Tentar DB primeiro
        if self._check_db_available():
            try:
                from .models import FeatureFlagConfig as FlagModel
                for db_flag in FlagModel.objects.filter(active=True):
                    flags[db_flag.name] = FeatureFlagConfig(
                        name=db_flag.name,
                        enabled=db_flag.enabled,
                        shadow_mode=db_flag.shadow_mode,
                        allowlist=db_flag.allowlist or [],
                        denylist=db_flag.denylist or [],
                        percent_rollout=db_flag.percent_rollout or 0,
                        metadata=db_flag.metadata or {},
                    )
            except Exception as e:
                logger.warning(f"Erro ao listar flags do DB: {e}")
        
        # Adicionar flags de env vars que não estão no DB
        from .settings import FEATURE_FLAGS
        for flag_name in FEATURE_FLAGS:
            if flag_name not in flags:
                config = get_feature_flag(flag_name)
                if config:
                    flags[flag_name] = config
        
        return flags


# Singleton
_storage_instance: Optional[FlagStorage] = None


def get_flag_storage() -> FlagStorage:
    """Obtém instância singleton do storage"""
    global _storage_instance
    if _storage_instance is None:
        _storage_instance = FlagStorage()
    return _storage_instance
