from django.db import migrations


def seed_modules(apps, schema_editor):
    SinapCoreModule = apps.get_model("app_sinapcore", "SinapCoreModule")
    defaults = [
        {
            "name": "environmental",
            "enabled": True,
            "priority": 1,
            "description": "Estado ambiental (Redis / orbital environmental_indiciary).",
        },
        {
            "name": "cognitive",
            "enabled": False,
            "priority": 2,
            "description": "Reservado — implementação futura.",
        },
        {
            "name": "emotional",
            "enabled": False,
            "priority": 3,
            "description": "Reservado — implementação futura.",
        },
    ]
    for row in defaults:
        SinapCoreModule.objects.update_or_create(
            name=row["name"],
            defaults={
                "enabled": row["enabled"],
                "priority": row["priority"],
                "description": row["description"],
            },
        )


def unseed_modules(apps, schema_editor):
    SinapCoreModule = apps.get_model("app_sinapcore", "SinapCoreModule")
    SinapCoreModule.objects.filter(name__in=("environmental", "cognitive", "emotional")).delete()


class Migration(migrations.Migration):

    dependencies = [
        ("app_sinapcore", "0001_initial"),
    ]

    operations = [
        migrations.RunPython(seed_modules, unseed_modules),
    ]
