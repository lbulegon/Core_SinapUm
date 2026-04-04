from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("app_sinapcore", "0002_seed_default_modules"),
    ]

    operations = [
        migrations.CreateModel(
            name="SinapCoreLog",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("module", models.CharField(db_index=True, max_length=50)),
                ("decision", models.CharField(max_length=100)),
                ("action", models.CharField(blank=True, max_length=100, null=True)),
                ("context", models.JSONField(blank=True, null=True)),
                ("timestamp", models.DateTimeField(auto_now_add=True, db_index=True)),
            ],
            options={
                "verbose_name": "Log SinapCore",
                "verbose_name_plural": "Logs SinapCore",
                "ordering": ("-timestamp",),
            },
        ),
    ]
