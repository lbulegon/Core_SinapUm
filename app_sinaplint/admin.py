"""
Admin Django — API keys, repositórios, análises e uso.
(Billing: ver ``app_platform_billing`` no Admin.)
"""

from django.contrib import admin

from app_sinaplint.models_api import APIKey
from app_sinaplint.models_repository import Analysis, AnalysisDelta, Repository
from app_sinaplint.models_usage import Usage


@admin.register(APIKey)
class APIKeyAdmin(admin.ModelAdmin):
    list_display = ("user", "name", "key_short", "is_active", "created_at", "last_used_at")
    list_filter = ("is_active",)
    raw_id_fields = ("user",)
    readonly_fields = ("key", "created_at")

    @staticmethod
    def key_short(obj: APIKey) -> str:
        return f"{obj.key[:16]}…" if obj.key else "—"


@admin.register(Usage)
class UsageAdmin(admin.ModelAdmin):
    list_display = ("user", "month", "analyses_count")
    list_filter = ("month",)
    raw_id_fields = ("user",)


@admin.register(Repository)
class RepositoryAdmin(admin.ModelAdmin):
    list_display = ("name", "user", "provider", "url", "created_at")
    list_filter = ("provider",)
    raw_id_fields = ("user",)
    search_fields = ("name", "url")


@admin.register(Analysis)
class AnalysisAdmin(admin.ModelAdmin):
    list_display = ("repository", "score", "architecture_score", "branch", "created_at")
    list_filter = ("created_at",)
    raw_id_fields = ("repository",)


@admin.register(AnalysisDelta)
class AnalysisDeltaAdmin(admin.ModelAdmin):
    list_display = ("analysis", "score_change", "new_cycles", "coupling_increased")
    raw_id_fields = ("analysis",)
