# Generated manually — SinapLint SaaS (Plan, Subscription, APIKey, Usage)

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
            name="Plan",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.CharField(max_length=50)),
                ("slug", models.SlugField(max_length=32, unique=True)),
                ("price_id", models.CharField(blank=True, help_text="Stripe Price ID (vazio para Free)", max_length=100)),
                (
                    "max_analyses_per_month",
                    models.IntegerField(help_text="Limite mensal de análises; -1 = ilimitado"),
                ),
                ("is_public", models.BooleanField(default=True, help_text="Mostrar na UI de upgrade")),
                ("sort_order", models.PositiveSmallIntegerField(default=0)),
            ],
            options={
                "ordering": ("sort_order", "id"),
            },
        ),
        migrations.CreateModel(
            name="Subscription",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("stripe_customer_id", models.CharField(blank=True, db_index=True, max_length=120)),
                ("stripe_subscription_id", models.CharField(blank=True, db_index=True, max_length=120)),
                ("active", models.BooleanField(default=True)),
                ("current_period_end", models.DateTimeField(blank=True, null=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "plan",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="subscriptions",
                        to="app_sinaplint.plan",
                    ),
                ),
                (
                    "user",
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="sinaplint_subscription",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "verbose_name": "Assinatura SinapLint",
                "verbose_name_plural": "Assinaturas SinapLint",
            },
        ),
        migrations.CreateModel(
            name="APIKey",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.CharField(blank=True, help_text="Rótulo opcional", max_length=80)),
                ("key", models.CharField(db_index=True, editable=False, max_length=64, unique=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("last_used_at", models.DateTimeField(blank=True, null=True)),
                ("is_active", models.BooleanField(default=True)),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="sinaplint_api_keys",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "verbose_name": "API Key SinapLint",
                "verbose_name_plural": "API Keys SinapLint",
                "ordering": ("-created_at",),
            },
        ),
        migrations.CreateModel(
            name="Usage",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("month", models.DateField(db_index=True, help_text="Primeiro dia do mês (UTC)")),
                ("analyses_count", models.PositiveIntegerField(default=0)),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="sinaplint_usage_months",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "verbose_name": "Uso mensal SinapLint",
                "verbose_name_plural": "Usos mensais SinapLint",
            },
        ),
        migrations.AddConstraint(
            model_name="usage",
            constraint=models.UniqueConstraint(fields=("user", "month"), name="uniq_sinaplint_usage_user_month"),
        ),
    ]
