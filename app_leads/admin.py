"""
Admin do Lead Registry - Interface de gerenciamento.
"""
from django.contrib import admin
from .models import Lead, LeadEvent, ProjectCredential


@admin.register(ProjectCredential)
class ProjectCredentialAdmin(admin.ModelAdmin):
    """Admin para credenciais de projetos."""
    list_display = (
        "project_key",
        "is_active",
        "created_at",
        "updated_at",
    )
    search_fields = ("project_key",)
    list_filter = ("is_active", "created_at")
    readonly_fields = ("created_at", "updated_at")
    ordering = ("-created_at",)
    
    fieldsets = (
        ("Credenciais", {
            "fields": ("project_key", "project_secret", "is_active")
        }),
        ("Timestamps", {
            "fields": ("created_at", "updated_at")
        }),
    )


@admin.register(Lead)
class LeadAdmin(admin.ModelAdmin):
    """Admin para leads."""
    list_display = (
        "id",
        "nome",
        "whatsapp",
        "email",
        "cidade",
        "source_system",
        "source_entrypoint",
        "source_context",
        "lead_status",
        "is_opt_out",
        "created_at",
    )
    search_fields = ("nome", "email", "whatsapp", "cidade")
    list_filter = (
        "source_system",
        "source_entrypoint",
        "source_context",
        "lead_status",
        "is_opt_out",
        "created_at",
    )
    readonly_fields = ("created_at", "updated_at")
    ordering = ("-created_at",)
    
    fieldsets = (
        ("Dados Básicos", {
            "fields": ("nome", "email", "whatsapp", "cidade")
        }),
        ("Origem", {
            "fields": (
                "source_system",
                "source_entrypoint",
                "source_context"
            )
        }),
        ("UTM Parameters", {
            "fields": (
                "utm_source",
                "utm_campaign",
                "utm_medium",
                "utm_content"
            ),
            "classes": ("collapse",)
        }),
        ("Status", {
            "fields": ("lead_status", "is_opt_out")
        }),
        ("Timestamps", {
            "fields": ("created_at", "updated_at")
        }),
    )


@admin.register(LeadEvent)
class LeadEventAdmin(admin.ModelAdmin):
    """Admin para eventos de auditoria."""
    list_display = (
        "id",
        "lead",
        "event_type",
        "ip",
        "created_at",
    )
    search_fields = (
        "lead__email",
        "lead__whatsapp",
        "event_type",
        "ip",
    )
    list_filter = ("event_type", "created_at")
    readonly_fields = ("created_at",)
    ordering = ("-created_at",)
    
    fieldsets = (
        ("Evento", {
            "fields": ("lead", "event_type")
        }),
        ("Auditoria", {
            "fields": ("ip", "user_agent", "referrer")
        }),
        ("Timestamp", {
            "fields": ("created_at",)
        }),
    )
    
    def has_add_permission(self, request):
        """Eventos são criados automaticamente - não permitir criação manual."""
        return False

