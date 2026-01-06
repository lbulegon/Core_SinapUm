"""
Admin do WhatsApp Gateway
"""
from django.contrib import admin
from app_whatsapp.models import AppWhatsappEvent, AppWhatsappInstance


@admin.register(AppWhatsappEvent)
class AppWhatsappEventAdmin(admin.ModelAdmin):
    """Admin para eventos canônicos"""
    list_display = ['event_id', 'ts', 'provider', 'instance_key', 'type', 'shopper_id']
    list_filter = ['provider', 'type', 'ts']
    search_fields = ['instance_key', 'shopper_id', 'event_id']
    readonly_fields = ['event_id', 'ts', 'id']
    date_hierarchy = 'ts'
    
    def has_add_permission(self, request):
        return False  # Eventos são criados apenas via EventBus


@admin.register(AppWhatsappInstance)
class AppWhatsappInstanceAdmin(admin.ModelAdmin):
    """Admin para instâncias WhatsApp"""
    list_display = ['instance_key', 'provider', 'status', 'created_at', 'updated_at']
    list_filter = ['provider', 'status', 'created_at']
    search_fields = ['instance_key']
    readonly_fields = ['created_at', 'updated_at']
