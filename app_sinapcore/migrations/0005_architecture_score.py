from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("app_sinapcore", "0004_sinapcore_command"),
    ]

    operations = [
        migrations.CreateModel(
            name="ArchitectureScore",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("score", models.PositiveSmallIntegerField(db_index=True)),
                ("quality", models.CharField(db_index=True, max_length=24)),
                ("passed", models.BooleanField(db_index=True, default=False)),
                ("min_pass_score", models.PositiveSmallIntegerField(default=80)),
                ("details", models.JSONField(blank=True, null=True)),
                (
                    "source",
                    models.CharField(
                        default="validate_framework",
                        help_text="Origem da execução (ex.: validate_framework, shell).",
                        max_length=64,
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True, db_index=True)),
            ],
            options={
                "verbose_name": "Score arquitetural",
                "verbose_name_plural": "Scores arquiteturais",
                "ordering": ("-created_at",),
            },
        ),
    ]
