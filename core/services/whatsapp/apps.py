"""
App config para WhatsApp Gateway (apenas para migrations)
"""
from django.apps import AppConfig


class WhatsAppGatewayConfig(AppConfig):
    """Configuração do app WhatsApp Gateway (apenas para migrations)"""
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'core.services.whatsapp'
    verbose_name = 'WhatsApp Gateway'
    
    def ready(self):
        """Inicialização do app"""
        # Importar signals se eventos canônicos estiverem habilitados
        try:
            from django.conf import settings
            if getattr(settings, 'WHATSAPP_CANONICAL_EVENTS_ENABLED', False):
                import core.services.whatsapp.canonical.signals  # noqa
        except ImportError:
            pass
