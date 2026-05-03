# Copia Plan/Subscription legados para app_platform_billing antes de remover tabelas.

from django.db import migrations


def forwards(apps, schema_editor):
    SaaSProduct = apps.get_model("app_platform_billing", "SaaSProduct")
    CatalogPlan = apps.get_model("app_platform_billing", "CatalogPlan")
    PlatformSubscription = apps.get_model("app_platform_billing", "PlatformSubscription")
    Plan = apps.get_model("app_sinaplint", "Plan")
    Subscription = apps.get_model("app_sinaplint", "Subscription")

    prod, _ = SaaSProduct.objects.get_or_create(
        slug="sinaplint",
        defaults={
            "display_name": "SinapLint",
            "is_active": True,
            "notes": "Migrado de app_sinaplint.Plan",
        },
    )
    for p in Plan.objects.all().order_by("sort_order", "id"):
        CatalogPlan.objects.update_or_create(
            product=prod,
            slug=p.slug,
            defaults={
                "name": p.name,
                "stripe_price_id": p.stripe_price_id or "",
                "limits": {
                    "max_analyses_per_month": p.max_analyses_per_month,
                    "max_repos": p.max_repos,
                },
                "is_public": p.is_public,
                "sort_order": p.sort_order,
            },
        )
    for sub in Subscription.objects.all():
        cp = None
        if sub.plan_id:
            try:
                pl = Plan.objects.get(pk=sub.plan_id)
                cp = CatalogPlan.objects.filter(product=prod, slug=pl.slug).first()
            except Plan.DoesNotExist:
                cp = None
        PlatformSubscription.objects.update_or_create(
            user_id=sub.user_id,
            product=prod,
            defaults={
                "plan": cp,
                "stripe_customer_id": sub.stripe_customer_id or "",
                "stripe_subscription_id": sub.stripe_subscription_id or "",
                "status": sub.status,
                "current_period_end": sub.current_period_end,
            },
        )


def backwards(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ("app_sinaplint", "0002_repository_analysis_delta_plan_sub"),
        ("app_platform_billing", "0001_initial"),
    ]

    operations = [
        migrations.RunPython(forwards, backwards),
    ]
