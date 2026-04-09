from django.apps import AppConfig


class AgentCoreConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "agent_core"
    label = "agent_core"
    verbose_name = "Agent Core (PAOR)"

    def ready(self) -> None:
        from agent_core.registry.bootstrap import register_builtin_modules

        register_builtin_modules()
