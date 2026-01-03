# Generated migration para adicionar trace_id ao ToolCallLog (MCP-aware)

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app_mcp_tool_registry', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='toolcalllog',
            name='trace_id',
            field=models.CharField(blank=True, db_index=True, max_length=64, null=True),
        ),
        migrations.AddIndex(
            model_name='toolcalllog',
            index=models.Index(fields=['trace_id'], name='mcp_tool_c_trace_i_idx'),
        ),
    ]

