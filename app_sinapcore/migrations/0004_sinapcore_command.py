from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("app_sinapcore", "0003_sinapcore_log"),
    ]

    operations = [
        migrations.CreateModel(
            name="SinapCoreCommand",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("pending", "Pendente"),
                            ("running", "Em execução"),
                            ("done", "Concluído"),
                            ("failed", "Falhou"),
                        ],
                        default="pending",
                        max_length=20,
                    ),
                ),
                (
                    "command",
                    models.CharField(
                        choices=[
                            ("reduce_load", "Reduzir carga"),
                            ("pause_orders", "Pausar pedidos"),
                            ("normalize", "Normalizar operação"),
                        ],
                        max_length=50,
                    ),
                ),
                ("payload", models.JSONField(blank=True, null=True)),
                ("executed", models.BooleanField(default=False)),
                (
                    "source",
                    models.CharField(
                        default="manual",
                        help_text="manual | auto (EOC)",
                        max_length=20,
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
            ],
            options={
                "verbose_name": "Comando SinapCore",
                "verbose_name_plural": "Comandos SinapCore",
                "ordering": ("-created_at",),
            },
        ),
    ]
