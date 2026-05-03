# Generated manually for app_platform_billing

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="SaaSProduct",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("slug", models.SlugField(db_index=True, max_length=64, unique=True)),
                ("display_name", models.CharField(max_length=120)),
                ("is_active", models.BooleanField(default=True)),
                ("notes", models.TextField(blank=True, help_text="Interno: URL docs, contacto comercial, …")),
            ],
            options={
                "ordering": ("slug",),
            },
        ),
        migrations.CreateModel(
            name="CatalogPlan",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.CharField(max_length=80)),
                ("slug", models.SlugField(max_length=64)),
                (
                    "stripe_price_id",
                    models.CharField(
                        blank=True,
                        db_index=True,
                        help_text="Stripe Price ID; vazio = plano gratuito / só limites internos",
                        max_length=120,
                    ),
                ),
                (
                    "limits",
                    models.JSONField(
                        blank=True,
                        default=dict,
                        help_text='Limites por app, ex.: {"max_analyses_per_month": 100, "max_repos": 5}',
                    ),
                ),
                ("is_public", models.BooleanField(default=True, help_text="Listado em GET /plans/ para landing / upgrade")),
                ("sort_order", models.PositiveSmallIntegerField(default=0)),
                (
                    "product",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="plans",
                        to="app_platform_billing.saasproduct",
                    ),
                ),
            ],
            options={
                "ordering": ("product", "sort_order", "id"),
            },
        ),
        migrations.CreateModel(
            name="PlatformSubscription",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("stripe_customer_id", models.CharField(blank=True, db_index=True, max_length=120)),
                ("stripe_subscription_id", models.CharField(blank=True, db_index=True, max_length=120)),
                (
                    "status",
                    models.CharField(
                        default="none",
                        help_text="none, active, canceled, past_due, trialing, incomplete, …",
                        max_length=50,
                    ),
                ),
                ("current_period_end", models.DateTimeField(blank=True, null=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "plan",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="active_subscriptions",
                        to="app_platform_billing.catalogplan",
                    ),
                ),
                (
                    "product",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="subscriptions",
                        to="app_platform_billing.saasproduct",
                    ),
                ),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="platform_subscriptions",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "verbose_name": "Assinatura plataforma",
                "verbose_name_plural": "Assinaturas plataforma",
            },
        ),
        migrations.AddConstraint(
            model_name="catalogplan",
            constraint=models.UniqueConstraint(fields=("product", "slug"), name="platform_billing_unique_plan_slug_per_product"),
        ),
        migrations.AddConstraint(
            model_name="platformsubscription",
            constraint=models.UniqueConstraint(fields=("user", "product"), name="platform_billing_unique_user_product"),
        ),
    ]
