from django.contrib import admin
from .models import ClientApp, Tool, ToolVersion, ToolCallLog


@admin.register(ClientApp)
class ClientAppAdmin(admin.ModelAdmin):
    list_display = ['key', 'name', 'is_active', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['key', 'name']
    readonly_fields = ['api_key', 'created_at']


@admin.register(Tool)
class ToolAdmin(admin.ModelAdmin):
    list_display = ['name', 'is_active', 'current_version', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['name', 'description']
    filter_horizontal = ['allowed_clients']
    readonly_fields = ['created_at']


@admin.register(ToolVersion)
class ToolVersionAdmin(admin.ModelAdmin):
    list_display = ['tool', 'version', 'runtime', 'is_active', 'is_deprecated', 'created_at']
    list_filter = ['runtime', 'is_active', 'is_deprecated', 'created_at']
    search_fields = ['tool__name', 'version', 'prompt_ref']
    readonly_fields = ['created_at']


@admin.register(ToolCallLog)
class ToolCallLogAdmin(admin.ModelAdmin):
    list_display = ['request_id', 'tool', 'version', 'client_key', 'ok', 'latency_ms', 'created_at']
    list_filter = ['ok', 'created_at', 'tool', 'version']
    search_fields = ['request_id', 'tool', 'client_key']
    readonly_fields = ['created_at']
    date_hierarchy = 'created_at'

