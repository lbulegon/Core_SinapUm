"""
Feature Flags Models
====================

Models Django para armazenamento de feature flags em banco de dados.
"""

from django.db import models
from django.utils import timezone
import json


class FeatureFlagConfig(models.Model):
    """
    Configuração de feature flag armazenada em banco
    
    Permite alterar flags sem fazer deploy (via admin ou API).
    """
    
    name = models.CharField(
        max_length=255,
        unique=True,
        db_index=True,
        help_text="Nome da feature flag"
    )
    
    enabled = models.BooleanField(
        default=False,
        help_text="Se flag está globalmente habilitada"
    )
    
    shadow_mode = models.BooleanField(
        default=False,
        help_text="Se flag está em shadow mode (não interfere no fluxo)"
    )
    
    allowlist = models.JSONField(
        default=list,
        blank=True,
        help_text="Lista de shopper_ids habilitados (JSON array)"
    )
    
    denylist = models.JSONField(
        default=list,
        blank=True,
        help_text="Lista de shopper_ids bloqueados (JSON array)"
    )
    
    percent_rollout = models.IntegerField(
        default=0,
        help_text="Percentual de rollout (0-100)"
    )
    
    metadata = models.JSONField(
        default=dict,
        blank=True,
        help_text="Metadados adicionais (JSON object)"
    )
    
    active = models.BooleanField(
        default=True,
        db_index=True,
        help_text="Se configuração está ativa"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        help_text="Usuário que criou a flag"
    )
    updated_by = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        help_text="Usuário que atualizou a flag"
    )
    
    class Meta:
        db_table = 'core_feature_flag_config'
        verbose_name = 'Feature Flag Config'
        verbose_name_plural = 'Feature Flag Configs'
        indexes = [
            models.Index(fields=['name', 'active']),
            models.Index(fields=['active', 'enabled']),
        ]
    
    def __str__(self):
        status = "enabled" if self.enabled else "disabled"
        shadow = " (shadow)" if self.shadow_mode else ""
        return f"{self.name}: {status}{shadow}"
    
    def to_dict(self) -> dict:
        """Converte para dicionário"""
        return {
            'name': self.name,
            'enabled': self.enabled,
            'shadow_mode': self.shadow_mode,
            'allowlist': self.allowlist or [],
            'denylist': self.denylist or [],
            'percent_rollout': self.percent_rollout,
            'metadata': self.metadata or {},
            'active': self.active,
        }
