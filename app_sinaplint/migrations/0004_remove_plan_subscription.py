from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("app_sinaplint", "0003_migrate_billing_to_platform"),
    ]

    operations = [
        migrations.DeleteModel(name="Subscription"),
        migrations.DeleteModel(name="Plan"),
    ]
