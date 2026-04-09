# Fase 4 — feedback estratégico

import uuid

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("app_inbound_events", "0004_cognitive_autonomy_models"),
    ]

    operations = [
        migrations.CreateModel(
            name="StrategyFeedbackRecord",
            fields=[
                ("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ("tenant_id", models.CharField(db_index=True, max_length=64)),
                ("strategy_key", models.CharField(db_index=True, max_length=128)),
                ("proposal_id", models.CharField(blank=True, max_length=128)),
                ("predicted_impact", models.FloatField(default=0.0)),
                ("realized_impact", models.FloatField(blank=True, null=True)),
                ("variance", models.FloatField(blank=True, null=True)),
                ("payload_json", models.JSONField(blank=True, default=dict)),
                ("created_at", models.DateTimeField(auto_now_add=True, db_index=True)),
            ],
            options={
                "ordering": ["-created_at"],
            },
        ),
    ]
