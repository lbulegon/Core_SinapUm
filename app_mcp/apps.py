# ============================================================================
# ARQUITETURA NOVA - app_mcp
# ============================================================================

from django.apps import AppConfig


class AppMcpConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'app_mcp'
    verbose_name = 'MCP Tools (Nova Arquitetura)'

