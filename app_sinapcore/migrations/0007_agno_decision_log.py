from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("app_sinapcore", "0006_sinaplint_cloud"),
    ]

    operations = [
        migrations.CreateModel(
            name="AgnoDecisionLog",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("module", models.CharField(db_index=True, max_length=40)),
                ("action", models.CharField(db_index=True, max_length=80)),
                ("product_id", models.IntegerField(blank=True, db_index=True, null=True)),
                ("product_name", models.CharField(blank=True, max_length=120)),
                ("reason", models.CharField(max_length=255)),
                ("payload", models.JSONField(blank=True, null=True)),
                ("created_at", models.DateTimeField(auto_now_add=True, db_index=True)),
            ],
            options={
                "verbose_name": "Log de decisao Agno",
                "verbose_name_plural": "Logs de decisao Agno",
                "ordering": ("-created_at",),
            },
        ),
    ]
