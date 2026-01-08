"""
Feature Flags & Rollout Manager
================================

Sistema de feature flags com rollout gradual e seguro.
Suporta ativação por allowlist, denylist, percentual e shadow mode.
"""

from .rollout import (
    is_enabled,
    get_rollout_manager,
    RolloutManager,
)
from .settings import (
    get_feature_flag,
    FeatureFlagConfig,
)
from .storage import (
    get_flag_storage,
    FlagStorage,
)

__all__ = [
    'is_enabled',
    'get_rollout_manager',
    'RolloutManager',
    'get_feature_flag',
    'FeatureFlagConfig',
    'get_flag_storage',
    'FlagStorage',
]
