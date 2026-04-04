from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("app_sinapcore", "0005_architecture_score"),
    ]

    operations = [
        migrations.CreateModel(
            name="SinapLintTenant",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.CharField(max_length=120)),
                ("api_key", models.CharField(db_index=True, editable=False, max_length=128, unique=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("is_active", models.BooleanField(default=True)),
            ],
            options={
                "verbose_name": "Tenant SinapLint",
                "verbose_name_plural": "Tenants SinapLint",
            },
        ),
        migrations.CreateModel(
            name="SinapLintProject",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.CharField(max_length=120)),
                ("repo_url", models.URLField(blank=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                (
                    "tenant",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="sinaplint_projects",
                        to="app_sinapcore.sinaplinttenant",
                    ),
                ),
            ],
            options={
                "verbose_name": "Projeto SinapLint",
                "verbose_name_plural": "Projetos SinapLint",
                "unique_together": {("tenant", "name")},
            },
        ),
        migrations.CreateModel(
            name="SinapLintAnalysis",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("score", models.PositiveSmallIntegerField()),
                ("result", models.JSONField()),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                (
                    "project",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="analyses",
                        to="app_sinapcore.sinaplintproject",
                    ),
                ),
            ],
            options={
                "verbose_name": "Análise SinapLint",
                "verbose_name_plural": "Análises SinapLint",
                "ordering": ("-created_at",),
            },
        ),
    ]
