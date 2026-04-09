# Generated manually — Fase 2 cognitive feedback loop

import uuid

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("app_inbound_events", "0002_decisionlog"),
    ]

    operations = [
        migrations.CreateModel(
            name="DecisionFeedbackRecord",
            fields=[
                ("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ("trace_id", models.CharField(db_index=True, max_length=128)),
                ("tenant_id", models.CharField(blank=True, db_index=True, max_length=64)),
                ("source", models.CharField(db_index=True, max_length=64)),
                ("decision_action", models.CharField(max_length=128)),
                ("decision_json", models.JSONField(blank=True, default=dict)),
                ("predicted_json", models.JSONField(blank=True, default=dict)),
                ("outcome_json", models.JSONField(blank=True, default=dict)),
                ("was_effective", models.BooleanField(blank=True, null=True)),
                ("impact_score", models.FloatField(blank=True, null=True)),
                ("decision_score_posterior", models.FloatField(blank=True, null=True)),
                ("created_at", models.DateTimeField(auto_now_add=True, db_index=True)),
                ("evaluated_at", models.DateTimeField(blank=True, null=True)),
            ],
            options={
                "ordering": ["-created_at"],
            },
        ),
    ]
