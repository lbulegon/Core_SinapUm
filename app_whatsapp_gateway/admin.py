# ============================================================================
# ARQUITETURA NOVA - app_whatsapp_gateway
# ============================================================================

from django.contrib import admin
from .models import EvolutionInstance, WebhookEvent


@admin.register(EvolutionInstance)
class EvolutionInstanceAdmin(admin.ModelAdmin):
    list_display = ['instance_id', 'shopper_id', 'status', 'phone_number', 'is_active', 'created_at']
    list_filter = ['status', 'is_active', 'created_at']
    search_fields = ['instance_id', 'shopper_id', 'phone_number']
    readonly_fields = ['id', 'created_at', 'updated_at', 'last_sync']
    
    fieldsets = (
        ('Identificação', {
            'fields': ('id', 'shopper_id', 'instance_id')
        }),
        ('Status', {
            'fields': ('status', 'is_active')
        }),
        ('QR Code', {
            'fields': ('qrcode', 'qrcode_url')
        }),
        ('WhatsApp', {
            'fields': ('phone_number', 'phone_name')
        }),
        ('Metadados', {
            'fields': ('metadata', 'last_sync', 'created_at', 'updated_at')
        }),
    )


@admin.register(WebhookEvent)
class WebhookEventAdmin(admin.ModelAdmin):
    list_display = ['event_type', 'instance', 'processed', 'created_at']
    list_filter = ['event_type', 'processed', 'created_at']
    search_fields = ['instance__instance_id', 'event_type']
    readonly_fields = ['id', 'created_at']
    
    fieldsets = (
        ('Evento', {
            'fields': ('id', 'instance', 'event_type', 'processed')
        }),
        ('Payload', {
            'fields': ('raw_payload', 'error_message')
        }),
        ('Timestamps', {
            'fields': ('created_at',)
        }),
    )

