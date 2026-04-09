from django.apps import AppConfig


class AppMcpToolRegistryConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'app_mcp_tool_registry'
    verbose_name = 'MCP Tool Registry'

    def ready(self):
        try:
            from adapters.register_resources import register_all_resource_handlers
            register_all_resource_handlers()
        except Exception:
            pass