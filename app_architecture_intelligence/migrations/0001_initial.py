# Generated manually for app_architecture_intelligence

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="ArchitectureCycle",
            fields=[
                ("id", models.CharField(editable=False, max_length=36, primary_key=True, serialize=False)),
                ("cycle_type", models.CharField(max_length=64)),
                ("state", models.CharField(max_length=32)),
                ("artifact_content", models.TextField()),
                ("artifact_type", models.CharField(default="document", max_length=64)),
                ("artifact_domain_id", models.CharField(blank=True, max_length=255, null=True)),
                ("artifact_metadata", models.JSONField(blank=True, default=dict)),
                ("trace_id", models.CharField(blank=True, max_length=255, null=True)),
                ("started_at", models.DateTimeField(blank=True, null=True)),
                ("completed_at", models.DateTimeField(blank=True, null=True)),
                ("metadata", models.JSONField(blank=True, default=dict)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
            ],
            options={
                "db_table": "architecture_cycles",
                "ordering": ["-created_at"],
            },
        ),
        migrations.CreateModel(
            name="ArchitectureStageRun",
            fields=[
                ("id", models.CharField(editable=False, max_length=36, primary_key=True, serialize=False)),
                ("stage", models.CharField(max_length=64)),
                ("state", models.CharField(max_length=32)),
                ("input_content", models.TextField()),
                ("output_content", models.TextField(default="")),
                ("started_at", models.DateTimeField(blank=True, null=True)),
                ("completed_at", models.DateTimeField(blank=True, null=True)),
                ("error_message", models.TextField(blank=True, null=True)),
                ("metadata", models.JSONField(blank=True, default=dict)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("cycle", models.ForeignKey(db_column="cycle_id", on_delete=django.db.models.deletion.CASCADE, related_name="stage_runs", to="app_architecture_intelligence.architecturecycle")),
            ],
            options={
                "db_table": "architecture_stage_runs",
                "ordering": ["created_at"],
            },
        ),
        migrations.CreateModel(
            name="ArchitectureDecisionLog",
            fields=[
                ("id", models.CharField(editable=False, max_length=36, primary_key=True, serialize=False)),
                ("stage", models.CharField(max_length=64)),
                ("decision", models.TextField()),
                ("rationale", models.TextField()),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("cycle", models.ForeignKey(db_column="cycle_id", on_delete=django.db.models.deletion.CASCADE, related_name="decisions", to="app_architecture_intelligence.architecturecycle")),
            ],
            options={
                "db_table": "architecture_decisions",
                "ordering": ["-created_at"],
            },
        ),
        migrations.CreateModel(
            name="ArchitectureRisk",
            fields=[
                ("id", models.CharField(editable=False, max_length=36, primary_key=True, serialize=False)),
                ("stage", models.CharField(max_length=64)),
                ("risk_description", models.TextField()),
                ("severity", models.CharField(max_length=32)),
                ("mitigation", models.TextField(blank=True, null=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("cycle", models.ForeignKey(db_column="cycle_id", on_delete=django.db.models.deletion.CASCADE, related_name="risks", to="app_architecture_intelligence.architecturecycle")),
            ],
            options={
                "db_table": "architecture_risks",
                "ordering": ["-created_at"],
            },
        ),
    ]
