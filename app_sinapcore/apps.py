from django.apps import AppConfig


class AppSinapcoreConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "app_sinapcore"
    label = "app_sinapcore"
    verbose_name = "SinapCore (módulos cognitivos)"

    def ready(self) -> None:
        from command_engine.bootstrap import register_handlers

        register_handlers()
