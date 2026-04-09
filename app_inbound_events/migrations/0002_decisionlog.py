# Generated manually — DecisionLog para learning no flow cognitivo

import uuid

import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("app_inbound_events", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="DecisionLog",
            fields=[
                ("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ("event_id", models.CharField(db_index=True, max_length=128)),
                ("source", models.CharField(db_index=True, default="task_queue_flow", max_length=64)),
                ("contexto_json", models.JSONField(blank=True, default=dict)),
                ("decisao_json", models.JSONField(blank=True, default=dict)),
                ("resultado_json", models.JSONField(blank=True, default=dict)),
                ("recorded_at", models.DateTimeField(db_index=True, default=django.utils.timezone.now)),
            ],
            options={
                "ordering": ["-recorded_at"],
            },
        ),
    ]
