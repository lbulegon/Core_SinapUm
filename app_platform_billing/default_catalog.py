"""Planos por omissão do produto ``sinaplint`` (catálogo plataforma)."""

from __future__ import annotations

DEFAULT_SINAPLINT_PLANS: list[dict] = [
    {
        "name": "Free",
        "slug": "free",
        "stripe_price_id": "",
        "max_analyses_per_month": 10,
        "max_repos": 5,
        "sort_order": 0,
    },
    {
        "name": "Pro",
        "slug": "pro",
        "stripe_price_id": "",
        "max_analyses_per_month": 200,
        "max_repos": 25,
        "sort_order": 10,
    },
    {
        "name": "Scale",
        "slug": "scale",
        "stripe_price_id": "",
        "max_analyses_per_month": -1,
        "max_repos": 500,
        "sort_order": 20,
    },
]


def upsert_sinaplint_catalog_plans() -> tuple[int, int]:
    """
    Garante ``SaaSProduct`` sinaplint e planos em ``CatalogPlan``.
    Devolve ``(total_planos, criados_nesta_execução)`` aproximado (criados = update_or_create created).
    """
    from app_platform_billing.models import CatalogPlan, SaaSProduct

    prod, _ = SaaSProduct.objects.get_or_create(
        slug="sinaplint",
        defaults={
            "display_name": "SinapLint",
            "is_active": True,
            "notes": "Catálogo SinapLint",
        },
    )
    created_n = 0
    for row in DEFAULT_SINAPLINT_PLANS:
        slug = row["slug"]
        lim = {
            "max_analyses_per_month": row["max_analyses_per_month"],
            "max_repos": row["max_repos"],
        }
        _, created = CatalogPlan.objects.update_or_create(
            product=prod,
            slug=slug,
            defaults={
                "name": row["name"],
                "stripe_price_id": row.get("stripe_price_id") or "",
                "limits": lim,
                "is_public": True,
                "sort_order": row["sort_order"],
            },
        )
        if created:
            created_n += 1
    total = CatalogPlan.objects.filter(product=prod).count()
    return total, created_n
