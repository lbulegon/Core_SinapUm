# Generated manually for SinapCoreModule

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="SinapCoreModule",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.CharField(choices=[("environmental", "Environmental"), ("cognitive", "Cognitive"), ("emotional", "Emotional"), ("semiotic", "Semiotic"), ("csv", "CSV")], max_length=50, unique=True)),
                ("enabled", models.BooleanField(default=True)),
                ("priority", models.IntegerField(default=1)),
                ("config", models.JSONField(blank=True, help_text="Parâmetros opcionais por módulo (JSON).", null=True)),
                ("description", models.TextField(blank=True, help_text="Documentação interna do módulo.")),
                ("updated_at", models.DateTimeField(auto_now=True)),
            ],
            options={
                "verbose_name": "Módulo SinapCore",
                "verbose_name_plural": "Módulos SinapCore",
                "ordering": ("priority", "name"),
            },
        ),
    ]
