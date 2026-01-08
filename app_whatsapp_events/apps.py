"""
App config para WhatsApp Events
"""
from django.apps import AppConfig


class AppWhatsappEventsConfig(AppConfig):
    """Configuração do app WhatsApp Events"""
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'app_whatsapp_events'
    verbose_name = 'WhatsApp Events'
    
    def ready(self):
        """Inicialização do app"""
        import app_whatsapp_events.signals  # noqa
