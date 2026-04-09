# PR5: idempotência declarativa por tool (ToolVersion)

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app_mcp_tool_registry', '0004_add_telemetry_to_tool_call_log'),
    ]

    operations = [
        migrations.AddField(
            model_name='toolversion',
            name='is_idempotent',
            field=models.BooleanField(default=False),
        ),
    ]
