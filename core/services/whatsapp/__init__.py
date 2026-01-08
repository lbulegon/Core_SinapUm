"""
WhatsApp Gateway - Camada de Abstração Padrão
=============================================

Camada de abstração para envio de mensagens WhatsApp.
Permite trocar providers sem alterar código que usa o gateway.

NOTA: Esta é uma camada ADITIVA. Não altera código existente.
Apenas permite que novos serviços usem uma interface padronizada.
"""
from .gateway import WhatsAppGateway, get_whatsapp_gateway
from .interfaces import IWhatsAppProvider, ProviderResult, ProviderHealth
from .exceptions import WhatsAppProviderError, WhatsAppProviderNotAvailable

__all__ = [
    'WhatsAppGateway',
    'get_whatsapp_gateway',
    'IWhatsAppProvider',
    'ProviderResult',
    'ProviderHealth',
    'WhatsAppProviderError',
    'WhatsAppProviderNotAvailable',
]
