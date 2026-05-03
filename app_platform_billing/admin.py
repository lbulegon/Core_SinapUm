"""
Admin Django — billing Stripe (catálogo + assinaturas).
Secção no índice: **Billing plataforma (Stripe)**.
"""

from django.contrib import admin

from app_platform_billing.models import CatalogPlan, PlatformSubscription, SaaSProduct


class CatalogPlanInline(admin.TabularInline):
    model = CatalogPlan
    extra = 0


@admin.register(SaaSProduct)
class SaaSProductAdmin(admin.ModelAdmin):
    list_display = ("slug", "display_name", "is_active")
    list_filter = ("is_active",)
    search_fields = ("slug", "display_name")
    inlines = [CatalogPlanInline]


@admin.register(CatalogPlan)
class CatalogPlanAdmin(admin.ModelAdmin):
    list_display = ("product", "name", "slug", "stripe_price_id", "is_public", "sort_order")
    list_filter = ("product", "is_public")
    search_fields = ("name", "slug", "stripe_price_id")


@admin.register(PlatformSubscription)
class PlatformSubscriptionAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "product",
        "plan",
        "status",
        "stripe_customer_id",
        "current_period_end",
    )
    list_filter = ("product", "status")
    search_fields = ("user__email", "stripe_customer_id", "stripe_subscription_id")
    raw_id_fields = ("user",)
