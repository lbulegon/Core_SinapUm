# ============================================================================
# ARQUITETURA NOVA - app_conversations
# ============================================================================

from django.contrib import admin
from .models import Conversation, Message, Suggestion


@admin.register(Conversation)
class ConversationAdmin(admin.ModelAdmin):
    list_display = ['conversation_key', 'shopper_id', 'customer_phone', 'mode', 'owner', 'last_message_at']
    list_filter = ['chat_type', 'mode', 'owner', 'created_at']
    search_fields = ['conversation_key', 'shopper_id', 'customer_phone', 'customer_name']
    readonly_fields = ['id', 'created_at', 'updated_at']
    
    fieldsets = (
        ('Identificação', {
            'fields': ('id', 'shopper_id', 'instance_id', 'conversation_key')
        }),
        ('Cliente', {
            'fields': ('customer_phone', 'customer_name')
        }),
        ('Tipo', {
            'fields': ('chat_type',)
        }),
        ('Controle', {
            'fields': ('owner', 'mode', 'tags')
        }),
        ('Timestamps', {
            'fields': ('last_message_at', 'created_at', 'updated_at')
        }),
    )


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ['conversation', 'direction', 'message_type', 'sent_by', 'timestamp']
    list_filter = ['direction', 'message_type', 'sent_by', 'timestamp']
    search_fields = ['conversation__conversation_key', 'text']
    readonly_fields = ['id', 'created_at']
    
    fieldsets = (
        ('Mensagem', {
            'fields': ('id', 'conversation', 'direction', 'message_type', 'sent_by')
        }),
        ('Conteúdo', {
            'fields': ('text', 'media_url')
        }),
        ('Metadados', {
            'fields': ('provider', 'raw_payload', 'timestamp', 'created_at')
        }),
    )


@admin.register(Suggestion)
class SuggestionAdmin(admin.ModelAdmin):
    list_display = ['conversation', 'intent', 'confidence', 'status', 'created_at']
    list_filter = ['status', 'intent', 'created_at']
    search_fields = ['conversation__conversation_key', 'intent', 'suggested_reply']
    readonly_fields = ['id', 'created_at']
    
    fieldsets = (
        ('Sugestão', {
            'fields': ('id', 'conversation', 'status')
        }),
        ('Análise IA', {
            'fields': ('intent', 'confidence')
        }),
        ('Conteúdo', {
            'fields': ('suggested_reply', 'actions')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'sent_at')
        }),
    )

