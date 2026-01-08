"""
Feature Flags Admin
==================

Interface Django Admin para gerenciar feature flags.
"""

from django.contrib import admin
from .models import FeatureFlagConfig


@admin.register(FeatureFlagConfig)
class FeatureFlagConfigAdmin(admin.ModelAdmin):
    """
    Admin para FeatureFlagConfig
    """
    
    list_display = [
        'name',
        'enabled',
        'shadow_mode',
        'percent_rollout',
        'allowlist_count',
        'denylist_count',
        'active',
        'updated_at',
    ]
    
    list_filter = [
        'enabled',
        'shadow_mode',
        'active',
        'created_at',
        'updated_at',
    ]
    
    search_fields = ['name']
    
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Informações Básicas', {
            'fields': ('name', 'active', 'enabled', 'shadow_mode')
        }),
        ('Rollout', {
            'fields': ('allowlist', 'denylist', 'percent_rollout'),
            'description': 'Configure rollout gradual por shopper_id'
        }),
        ('Metadados', {
            'fields': ('metadata',),
            'classes': ('collapse',)
        }),
        ('Auditoria', {
            'fields': ('created_at', 'updated_at', 'created_by', 'updated_by'),
            'classes': ('collapse',)
        }),
    )
    
    def allowlist_count(self, obj):
        """Conta itens na allowlist"""
        return len(obj.allowlist or [])
    allowlist_count.short_description = 'Allowlist'
    
    def denylist_count(self, obj):
        """Conta itens na denylist"""
        return len(obj.denylist or [])
    denylist_count.short_description = 'Denylist'
    
    def save_model(self, request, obj, form, change):
        """Salva model e registra usuário"""
        if change:
            obj.updated_by = request.user.username if request.user.is_authenticated else 'system'
        else:
            obj.created_by = request.user.username if request.user.is_authenticated else 'system'
            obj.updated_by = request.user.username if request.user.is_authenticated else 'system'
        
        super().save_model(request, obj, form, change)
        
        # Limpar cache do rollout manager
        try:
            from .rollout import get_rollout_manager
            manager = get_rollout_manager()
            manager._clear_cache(obj.name)
        except Exception:
            pass
