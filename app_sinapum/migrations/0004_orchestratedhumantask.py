import uuid

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("app_sinapum", "0003_add_sistema_and_prompt_sistema"),
    ]

    operations = [
        migrations.CreateModel(
            name="OrchestratedHumanTask",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("orchestration_id", models.UUIDField(db_index=True, default=uuid.uuid4, editable=False, unique=True)),
                ("title", models.CharField(max_length=255)),
                ("body", models.TextField()),
                ("min_responses", models.PositiveSmallIntegerField(default=3)),
                ("status", models.CharField(choices=[("open", "Aberta"), ("result_received", "Resultado recebido")], db_index=True, default="open", max_length=32)),
                ("result_payload", models.JSONField(blank=True, null=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
            ],
            options={
                "verbose_name": "Tarefa humana orquestrada (MarketFish)",
                "verbose_name_plural": "Tarefas humanas orquestradas (MarketFish)",
                "ordering": ["-id"],
            },
        ),
    ]
