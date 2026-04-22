from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("app_sinapcore", "0007_agno_decision_log"),
    ]

    operations = [
        migrations.CreateModel(
            name="PricingLog",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("empresa_id", models.IntegerField(blank=True, db_index=True, null=True)),
                ("produto_id", models.IntegerField(db_index=True)),
                ("preco_base", models.DecimalField(decimal_places=2, max_digits=12)),
                ("preco_final", models.DecimalField(decimal_places=2, max_digits=12)),
                ("fator_total", models.DecimalField(decimal_places=4, max_digits=10)),
                ("fatores", models.JSONField(default=dict)),
                ("canal", models.CharField(default="app", max_length=50)),
                ("motivo", models.TextField(blank=True)),
                ("timestamp", models.DateTimeField(auto_now_add=True, db_index=True)),
            ],
            options={
                "ordering": ["-timestamp"],
                "verbose_name": "Log de precificação (Agno)",
                "verbose_name_plural": "Logs de precificação (Agno)",
            },
        ),
        migrations.AddIndex(
            model_name="pricinglog",
            index=models.Index(fields=["empresa_id", "-timestamp"], name="app_sinapco_empresa_8f3a1b_idx"),
        ),
        migrations.AddIndex(
            model_name="pricinglog",
            index=models.Index(fields=["produto_id", "-timestamp"], name="app_sinapco_produto_2c9e4d_idx"),
        ),
    ]
