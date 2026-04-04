from django.contrib import admin

from app_sinapcore.models.architecture_score import ArchitectureScore
from app_sinapcore.models.sinapcore_command import SinapCoreCommand
from app_sinapcore.models.sinapcore_log import SinapCoreLog
from app_sinapcore.models.sinapcore_module import SinapCoreModule
from app_sinapcore.models.sinaplint_cloud import (
    SinapLintAnalysis,
    SinapLintProject,
    SinapLintTenant,
)


@admin.register(ArchitectureScore)
class ArchitectureScoreAdmin(admin.ModelAdmin):
    list_display = ("created_at", "score", "quality", "passed", "min_pass_score", "source")
    list_filter = ("passed", "quality", "source")
    ordering = ("-created_at",)
    readonly_fields = ("created_at", "score", "quality", "passed", "min_pass_score", "details", "source")
    date_hierarchy = "created_at"

    def has_add_permission(self, request) -> bool:
        return False

    def has_change_permission(self, request, obj=None) -> bool:
        return False

    def has_delete_permission(self, request, obj=None) -> bool:
        return False


@admin.register(SinapCoreCommand)
class SinapCoreCommandAdmin(admin.ModelAdmin):
    list_display = ("created_at", "command", "status", "source", "executed")
    list_filter = ("command", "status", "source", "executed")
    ordering = ("-created_at",)
    readonly_fields = ("created_at",)


@admin.register(SinapCoreLog)
class SinapCoreLogAdmin(admin.ModelAdmin):
    list_display = ("timestamp", "module", "decision", "action")
    list_filter = ("module",)
    search_fields = ("decision", "action", "module")
    ordering = ("-timestamp",)
    readonly_fields = ("timestamp", "module", "decision", "action", "context")

    def has_add_permission(self, request) -> bool:
        return False


@admin.register(SinapLintTenant)
class SinapLintTenantAdmin(admin.ModelAdmin):
    list_display = ("name", "is_active", "created_at")
    list_filter = ("is_active",)
    readonly_fields = ("api_key", "created_at")
    search_fields = ("name",)


@admin.register(SinapLintProject)
class SinapLintProjectAdmin(admin.ModelAdmin):
    list_display = ("name", "tenant", "repo_url", "created_at")
    list_filter = ("tenant",)
    search_fields = ("name", "repo_url")


@admin.register(SinapLintAnalysis)
class SinapLintAnalysisAdmin(admin.ModelAdmin):
    list_display = ("id", "project", "score", "created_at")
    list_filter = ("project__tenant",)
    readonly_fields = ("project", "score", "result", "created_at")
    ordering = ("-created_at",)

    def has_add_permission(self, request) -> bool:
        return False


@admin.register(SinapCoreModule)
class SinapCoreModuleAdmin(admin.ModelAdmin):
    list_display = ("name", "enabled", "priority", "updated_at")
    list_editable = ("enabled", "priority")
    list_filter = ("enabled",)
    search_fields = ("name", "description")
    ordering = ("priority", "name")
    readonly_fields = ("updated_at",)
    fieldsets = (
        (None, {"fields": ("name", "enabled", "priority")}),
        ("Comportamento", {"fields": ("config", "description")}),
        ("Metadados", {"fields": ("updated_at",)}),
    )
