"""
Admin - WhatsApp Canonical Events v1.0
"""
from django.contrib import admin
from .models import CanonicalEventLog


@admin.register(CanonicalEventLog)
class CanonicalEventLogAdmin(admin.ModelAdmin):
    """Admin para CanonicalEventLog"""
    list_display = [
        'event_type', 'event_source', 'from_number', 'instance_key',
        'timestamp', 'created_at', 'shopper_id'
    ]
    list_filter = [
        'event_type', 'event_source', 'instance_key', 'timestamp', 'created_at'
    ]
    search_fields = [
        'event_id', 'from_number', 'to_number', 'message_id',
        'correlation_id', 'shopper_id', 'skm_id'
    ]
    readonly_fields = [
        'id', 'event_id', 'timestamp', 'created_at', 'processed_at'
    ]
    date_hierarchy = 'timestamp'
    
    fieldsets = (
        ('Identificação', {
            'fields': ('id', 'event_id', 'event_type', 'event_source', 'instance_key')
        }),
        ('Contexto', {
            'fields': ('timestamp', 'from_number', 'to_number', 'message_id')
        }),
        ('Metadados', {
            'fields': ('correlation_id', 'shopper_id', 'skm_id')
        }),
        ('Payload', {
            'fields': ('payload', 'raw_payload')
        }),
        ('Idempotência', {
            'fields': ('provider_event_id', 'provider_message_id')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'processed_at')
        }),
    )
