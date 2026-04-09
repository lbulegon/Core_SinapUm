# Migration: telemetria (tokens, custo, model, provider) em ToolCallLog — observabilidade MCP/ACP

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app_mcp_tool_registry', '0003_rename_mcp_tool_c_request_idx_mcp_tool_ca_request_125292_idx_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='toolcalllog',
            name='tokens_in',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='toolcalllog',
            name='tokens_out',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='toolcalllog',
            name='cost_usd',
            field=models.DecimalField(blank=True, decimal_places=6, max_digits=12, null=True),
        ),
        migrations.AddField(
            model_name='toolcalllog',
            name='model',
            field=models.CharField(blank=True, max_length=80),
        ),
        migrations.AddField(
            model_name='toolcalllog',
            name='provider',
            field=models.CharField(blank=True, max_length=80),
        ),
    ]
