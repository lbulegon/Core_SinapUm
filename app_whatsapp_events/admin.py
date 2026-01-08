"""
Admin - WhatsApp Events
"""
from django.contrib import admin
from .models import (
    WhatsAppEventLog,
    WhatsAppConversation,
    WhatsAppThreadParticipant,
    WhatsAppMessageIndex,
)


@admin.register(WhatsAppEventLog)
class WhatsAppEventLogAdmin(admin.ModelAdmin):
    """Admin para WhatsAppEventLog"""
    list_display = [
        'event_type', 'provider', 'actor_wa_id', 'thread_key',
        'occurred_at', 'shopper_id', 'skm_id'
    ]
    list_filter = [
        'event_type', 'provider', 'chat_type', 'message_direction',
        'occurred_at', 'created_at'
    ]
    search_fields = [
        'event_id', 'idempotency_key', 'actor_wa_id', 'thread_key',
        'conversation_id', 'shopper_id', 'skm_id', 'provider_message_id'
    ]
    readonly_fields = [
        'id', 'event_id', 'idempotency_key', 'occurred_at', 'created_at', 'processed_at'
    ]
    date_hierarchy = 'occurred_at'
    
    fieldsets = (
        ('Identificação', {
            'fields': ('id', 'event_id', 'event_type', 'event_version', 'occurred_at')
        }),
        ('Fonte', {
            'fields': ('provider', 'provider_account_id', 'provider_message_id', 'webhook_id')
        }),
        ('Idempotência', {
            'fields': ('idempotency_key', 'correlation_id', 'parent_event_id')
        }),
        ('Roteamento', {
            'fields': ('shopper_id', 'skm_id', 'keeper_id', 'conversation_id', 'thread_key')
        }),
        ('Ator', {
            'fields': ('actor_wa_id', 'actor_role')
        }),
        ('Contexto', {
            'fields': ('chat_type', 'group_id')
        }),
        ('Mensagem', {
            'fields': ('message_type', 'message_direction')
        }),
        ('Payloads', {
            'fields': ('payload_json', 'raw_provider_payload')
        }),
        ('Segurança', {
            'fields': ('signature_valid', 'risk_flags')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'processed_at')
        }),
    )


@admin.register(WhatsAppConversation)
class WhatsAppConversationAdmin(admin.ModelAdmin):
    """Admin para WhatsAppConversation"""
    list_display = [
        'conversation_id', 'thread_key', 'status', 'shopper_id', 'skm_id',
        'last_event_at', 'created_at'
    ]
    list_filter = ['status', 'created_at', 'last_event_at']
    search_fields = [
        'conversation_id', 'thread_key', 'shopper_id', 'skm_id', 'keeper_id'
    ]
    readonly_fields = ['id', 'conversation_id', 'thread_key', 'created_at', 'updated_at']
    date_hierarchy = 'last_event_at'
    
    fieldsets = (
        ('Identificação', {
            'fields': ('id', 'conversation_id', 'thread_key')
        }),
        ('Roteamento', {
            'fields': ('shopper_id', 'skm_id', 'keeper_id')
        }),
        ('Status', {
            'fields': ('status', 'last_event_at', 'last_actor_wa_id', 'closed_at')
        }),
        ('Metadados', {
            'fields': ('tags',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at')
        }),
    )


@admin.register(WhatsAppThreadParticipant)
class WhatsAppThreadParticipantAdmin(admin.ModelAdmin):
    """Admin para WhatsAppThreadParticipant"""
    list_display = [
        'wa_id', 'display_name', 'role', 'conversation', 'last_seen_at', 'is_blocked'
    ]
    list_filter = ['role', 'is_blocked', 'last_seen_at']
    search_fields = ['wa_id', 'display_name', 'conversation__conversation_id']
    readonly_fields = ['id', 'first_seen_at', 'last_seen_at']
    raw_id_fields = ['conversation']


@admin.register(WhatsAppMessageIndex)
class WhatsAppMessageIndexAdmin(admin.ModelAdmin):
    """Admin para WhatsAppMessageIndex"""
    list_display = [
        'provider_message_id', 'conversation', 'direction', 'message_type', 'occurred_at'
    ]
    list_filter = ['direction', 'message_type', 'occurred_at']
    search_fields = ['provider_message_id', 'conversation__conversation_id']
    readonly_fields = ['id', 'occurred_at']
    raw_id_fields = ['conversation']
