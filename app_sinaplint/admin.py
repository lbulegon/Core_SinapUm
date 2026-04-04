"""
Admin Django — planos, assinaturas, API keys e uso.
"""

from django.contrib import admin

from app_sinaplint.models_api import APIKey
from app_sinaplint.models_billing import Plan, Subscription
from app_sinaplint.models_repository import Analysis, AnalysisDelta, Repository
from app_sinaplint.models_usage import Usage


@admin.register(Plan)
class PlanAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "slug",
        "max_analyses_per_month",
        "max_repos",
        "stripe_price_id",
        "is_public",
        "sort_order",
    )
    list_filter = ("is_public",)
    search_fields = ("name", "slug", "stripe_price_id")


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ("user", "plan", "status", "stripe_customer_id", "current_period_end")
    list_filter = ("status",)
    raw_id_fields = ("user", "plan")


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
