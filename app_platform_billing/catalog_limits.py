"""Leitura de limites a partir de ``CatalogPlan.limits`` (JSON)."""

from __future__ import annotations

from app_platform_billing.models import CatalogPlan, PlatformSubscription, SaaSProduct

# Slug canónico do produto SinapLint no catálogo plataforma
SINAPLINT_PRODUCT_SLUG = "sinaplint"


def analyses_monthly_limit(plan: CatalogPlan) -> int:
    v = (plan.limits or {}).get("max_analyses_per_month")
    if v is None:
        return 0
    return int(v)


def repos_limit(plan: CatalogPlan) -> int:
    v = (plan.limits or {}).get("max_repos")
    if v is None:
        return 0
    return int(v)


def get_saas_product(slug: str) -> SaaSProduct | None:
    return SaaSProduct.objects.filter(slug=slug, is_active=True).first()


def get_platform_subscription(user_id: int, product_slug: str) -> PlatformSubscription | None:
    return (
        PlatformSubscription.objects.filter(
            user_id=user_id,
            product__slug=product_slug,
        )
        .select_related("plan", "product")
        .first()
    )


def get_free_catalog_plan(product: SaaSProduct) -> CatalogPlan | None:
    return CatalogPlan.objects.filter(product=product, slug="free", is_public=True).first()
