# SinapLint SaaS — repositórios, análises, delta; Plan.stripe_price_id + max_repos; Subscription.status

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


def copy_active_to_status(apps, schema_editor):
    Subscription = apps.get_model("app_sinaplint", "Subscription")
    for s in Subscription.objects.all():
        s.status = "active" if s.active else "canceled"
        s.save(update_fields=["status"])


def noop(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ("app_sinaplint", "0001_sinaplint_saas_billing_api_usage"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.RenameField(
            model_name="plan",
            old_name="price_id",
            new_name="stripe_price_id",
        ),
        migrations.AddField(
            model_name="plan",
            name="max_repos",
            field=models.PositiveIntegerField(
                default=5,
                help_text="Máximo de repositórios registados por utilizador",
            ),
        ),
        migrations.AddField(
            model_name="subscription",
            name="status",
            field=models.CharField(
                default="active",
                help_text="active, canceled, past_due, trialing, incomplete, …",
                max_length=50,
            ),
        ),
        migrations.RunPython(copy_active_to_status, noop),
        migrations.RemoveField(
            model_name="subscription",
            name="active",
        ),
        migrations.CreateModel(
            name="Repository",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.CharField(max_length=255)),
                ("url", models.URLField(max_length=500)),
                ("provider", models.CharField(default="github", max_length=50)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="sinaplint_repositories",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "verbose_name": "Repositório SinapLint",
                "verbose_name_plural": "Repositórios SinapLint",
            },
        ),
        migrations.AddConstraint(
            model_name="repository",
            constraint=models.UniqueConstraint(fields=("user", "url"), name="uniq_sinaplint_repo_user_url"),
        ),
        migrations.CreateModel(
            name="Analysis",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("commit_hash", models.CharField(blank=True, max_length=100, null=True)),
                ("branch", models.CharField(blank=True, max_length=100, null=True)),
                ("score", models.IntegerField()),
                ("architecture_score", models.IntegerField(blank=True, null=True)),
                ("result", models.JSONField()),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                (
                    "repository",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="analyses",
                        to="app_sinaplint.repository",
                    ),
                ),
            ],
            options={
                "ordering": ("-created_at",),
                "verbose_name": "Análise SinapLint",
                "verbose_name_plural": "Análises SinapLint",
            },
        ),
        migrations.CreateModel(
            name="AnalysisDelta",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("score_change", models.IntegerField(default=0)),
                ("new_cycles", models.IntegerField(default=0)),
                ("coupling_increased", models.BooleanField(default=False)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                (
                    "analysis",
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="delta",
                        to="app_sinaplint.analysis",
                    ),
                ),
            ],
            options={
                "verbose_name": "Delta de análise",
                "verbose_name_plural": "Deltas de análise",
            },
        ),
    ]
