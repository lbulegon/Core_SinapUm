# ACP — AgentTask initial migration

import uuid
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="AgentTask",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("task_id", models.UUIDField(db_index=True, default=uuid.uuid4, editable=False, unique=True)),
                ("agent_name", models.CharField(max_length=120)),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("PENDING", "Pendente"),
                            ("RUNNING", "Em execução"),
                            ("WAITING", "Aguardando"),
                            ("FAILED", "Falhou"),
                            ("COMPLETED", "Concluída"),
                            ("CANCELLED", "Cancelada"),
                        ],
                        db_index=True,
                        default="PENDING",
                        max_length=20,
                    ),
                ),
                ("payload", models.JSONField(default=dict)),
                ("result", models.JSONField(blank=True, null=True)),
                ("error", models.TextField(blank=True, null=True)),
                ("trace_id", models.CharField(blank=True, db_index=True, max_length=64, null=True)),
                ("retry_count", models.PositiveIntegerField(default=0)),
                ("max_retries", models.PositiveIntegerField(default=3)),
                ("timeout_seconds", models.PositiveIntegerField(blank=True, null=True)),
                ("idempotency_key", models.CharField(blank=True, db_index=True, max_length=255, null=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("started_at", models.DateTimeField(blank=True, null=True)),
                ("finished_at", models.DateTimeField(blank=True, null=True)),
            ],
            options={
                "db_table": "acp_agent_task",
                "ordering": ["-created_at"],
                "verbose_name": "Agent Task",
                "verbose_name_plural": "Agent Tasks",
            },
        ),
        migrations.AddIndex(
            model_name="agenttask",
            index=models.Index(fields=["status"], name="acp_agent_t_status_idx"),
        ),
        migrations.AddIndex(
            model_name="agenttask",
            index=models.Index(fields=["agent_name", "status"], name="acp_agent_t_agent_n_idx"),
        ),
        migrations.AddIndex(
            model_name="agenttask",
            index=models.Index(fields=["created_at"], name="acp_agent_t_created_idx"),
        ),
    ]
