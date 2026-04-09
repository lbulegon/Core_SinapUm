# Fase 3 — memória de padrões e log de ações autónomas

import uuid

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("app_inbound_events", "0003_decisionfeedbackrecord"),
    ]

    operations = [
        migrations.CreateModel(
            name="CognitivePatternMemory",
            fields=[
                ("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ("tenant_id", models.CharField(db_index=True, max_length=64)),
                ("trace_id", models.CharField(blank=True, db_index=True, max_length=128)),
                ("pattern_key", models.CharField(db_index=True, max_length=128)),
                ("confidence", models.FloatField(default=0.0)),
                ("signals_json", models.JSONField(blank=True, default=dict)),
                ("created_at", models.DateTimeField(auto_now_add=True, db_index=True)),
            ],
            options={
                "ordering": ["-created_at"],
            },
        ),
        migrations.CreateModel(
            name="AutonomyActionLog",
            fields=[
                ("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ("tenant_id", models.CharField(db_index=True, max_length=64)),
                ("trace_id", models.CharField(db_index=True, max_length=128)),
                ("proposal_key", models.CharField(max_length=128)),
                ("mcp_tool", models.CharField(blank=True, max_length=128)),
                ("decision_json", models.JSONField(blank=True, default=dict)),
                ("autonomy_level", models.PositiveSmallIntegerField(default=0)),
                ("status", models.CharField(db_index=True, max_length=32)),
                ("acp_task_id", models.CharField(blank=True, max_length=64)),
                ("outcome_json", models.JSONField(blank=True, default=dict)),
                ("created_at", models.DateTimeField(auto_now_add=True, db_index=True)),
            ],
            options={
                "ordering": ["-created_at"],
            },
        ),
    ]
