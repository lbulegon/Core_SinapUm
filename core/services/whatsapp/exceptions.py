"""
Exceptions - WhatsApp Gateway
==============================

Exceções padronizadas para o gateway WhatsApp.
"""


class WhatsAppProviderError(Exception):
    """Erro genérico do provider WhatsApp"""
    pass


class WhatsAppProviderNotAvailable(WhatsAppProviderError):
    """Provider não está disponível"""
    pass


class WhatsAppProviderConfigurationError(WhatsAppProviderError):
    """Erro de configuração do provider"""
    pass


class WhatsAppSendError(WhatsAppProviderError):
    """Erro ao enviar mensagem"""
    pass
