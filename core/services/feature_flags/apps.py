"""
Feature Flags App Config
========================
"""

from django.apps import AppConfig


class FeatureFlagsConfig(AppConfig):
    """App config para feature flags"""
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'core.services.feature_flags'
    verbose_name = 'Feature Flags & Rollout Manager'
