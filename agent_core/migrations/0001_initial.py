# Generated manually for Core_SinapUm — rode `makemigrations` se ajustar o modelo

import uuid

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies: list[tuple[str, str]] = []

    operations = [
        migrations.CreateModel(
            name="AgentRun",
            fields=[
                (
                    "id",
                    models.UUIDField(
                        default=uuid.uuid4,
                        editable=False,
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                ("objetivo", models.TextField()),
                ("estado_atual", models.JSONField(blank=True, default=dict)),
                ("plano", models.JSONField(blank=True, default=dict)),
                ("iteracao", models.PositiveIntegerField(default=0)),
                ("historico", models.JSONField(blank=True, default=list)),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("running", "Running"),
                            ("awaiting_human", "Awaiting human"),
                            ("completed", "Completed"),
                            ("failed", "Failed"),
                        ],
                        db_index=True,
                        default="running",
                        max_length=32,
                    ),
                ),
                ("error_message", models.TextField(blank=True, default="")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
            ],
            options={
                "verbose_name": "Agent run",
                "verbose_name_plural": "Agent runs",
                "ordering": ("-created_at",),
            },
        ),
    ]
