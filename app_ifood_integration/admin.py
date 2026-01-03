"""
Django Admin para app_ifood_integration
"""
from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from .models import IfoodStore, IfoodOAuthToken, IfoodSyncRun, MrfooOrder, MrfooPayout


@admin.register(IfoodStore)
class IfoodStoreAdmin(admin.ModelAdmin):
    list_display = ['nome', 'cnpj', 'ifood_merchant_id', 'ativo', 'has_valid_token_display', 'created_at']
    list_filter = ['ativo', 'created_at']
    search_fields = ['nome', 'cnpj', 'ifood_merchant_id']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Identificação', {
            'fields': ('nome', 'cnpj', 'ifood_merchant_id', 'ativo')
        }),
        ('Metadados', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def has_valid_token_display(self, obj):
        """Exibe status do token OAuth"""
        if obj.has_valid_token:
            return format_html('<span style="color: green;">✓ Token válido</span>')
        return format_html('<span style="color: red;">✗ Sem token válido</span>')
    has_valid_token_display.short_description = 'Token OAuth'


@admin.register(IfoodOAuthToken)
class IfoodOAuthTokenAdmin(admin.ModelAdmin):
    list_display = ['store', 'token_type', 'expires_at', 'is_expired_display', 'updated_at']
    list_filter = ['token_type', 'expires_at']
    search_fields = ['store__nome', 'store__ifood_merchant_id']
    readonly_fields = ['created_at', 'updated_at', 'access_token_masked', 'refresh_token_masked']
    
    fieldsets = (
        ('Loja', {
            'fields': ('store',)
        }),
        ('Tokens (criptografados)', {
            'fields': ('access_token_masked', 'refresh_token_masked', 'token_type', 'expires_at', 'scope'),
            'description': 'Os tokens são armazenados criptografados em produção.'
        }),
        ('Metadados', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def access_token_masked(self, obj):
        """Exibe token mascarado"""
        if obj.access_token:
            return f"{obj.access_token[:20]}...{obj.access_token[-10:]}"
        return "-"
    access_token_masked.short_description = 'Access Token (mascarado)'
    
    def refresh_token_masked(self, obj):
        """Exibe refresh token mascarado"""
        if obj.refresh_token:
            return f"{obj.refresh_token[:20]}...{obj.refresh_token[-10:]}"
        return "-"
    refresh_token_masked.short_description = 'Refresh Token (mascarado)'
    
    def is_expired_display(self, obj):
        """Exibe status de expiração"""
        if obj.is_expired():
            return format_html('<span style="color: red;">✗ Expirado</span>')
        return format_html('<span style="color: green;">✓ Válido</span>')
    is_expired_display.short_description = 'Status'


@admin.register(IfoodSyncRun)
class IfoodSyncRunAdmin(admin.ModelAdmin):
    list_display = ['store', 'kind', 'started_at', 'finished_at', 'ok', 'items_ingested', 'duration_display']
    list_filter = ['kind', 'ok', 'started_at']
    search_fields = ['store__nome', 'error']
    readonly_fields = ['started_at', 'finished_at', 'duration_display']
    date_hierarchy = 'started_at'
    
    fieldsets = (
        ('Sincronização', {
            'fields': ('store', 'kind', 'ok', 'items_ingested', 'error')
        }),
        ('Tempo', {
            'fields': ('started_at', 'finished_at', 'duration_display')
        }),
        ('Metadados', {
            'fields': ('metadata',),
            'classes': ('collapse',)
        }),
    )
    
    def duration_display(self, obj):
        """Exibe duração da sincronização"""
        if obj.duration_seconds:
            return f"{obj.duration_seconds:.2f}s"
        return "-"
    duration_display.short_description = 'Duração'


@admin.register(MrfooOrder)
class MrfooOrderAdmin(admin.ModelAdmin):
    list_display = ['order_id', 'store', 'created_at', 'status', 'total_value', 'channel', 'synced_at']
    list_filter = ['status', 'channel', 'created_at', 'synced_at']
    search_fields = ['order_id', 'store__nome']
    readonly_fields = ['synced_at', 'updated_at']
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('Identificação', {
            'fields': ('order_id', 'store', 'channel')
        }),
        ('Dados do Pedido', {
            'fields': ('created_at', 'status', 'total_value')
        }),
        ('Dados Brutos', {
            'fields': ('raw_json',),
            'classes': ('collapse',)
        }),
        ('Metadados', {
            'fields': ('synced_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(MrfooPayout)
class MrfooPayoutAdmin(admin.ModelAdmin):
    list_display = ['payout_id', 'store', 'reference_period', 'gross', 'fees', 'net', 'channel', 'synced_at']
    list_filter = ['channel', 'reference_period', 'synced_at']
    search_fields = ['payout_id', 'store__nome', 'reference_period']
    readonly_fields = ['synced_at', 'updated_at']
    
    fieldsets = (
        ('Identificação', {
            'fields': ('payout_id', 'store', 'channel', 'reference_period')
        }),
        ('Valores Financeiros', {
            'fields': ('gross', 'fees', 'net')
        }),
        ('Dados Brutos', {
            'fields': ('raw_json',),
            'classes': ('collapse',)
        }),
        ('Metadados', {
            'fields': ('synced_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

