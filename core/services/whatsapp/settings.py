"""
Settings - WhatsApp Gateway
===========================

Configurações e feature flags para o gateway WhatsApp.
"""
import os
from typing import List
from django.conf import settings


def get_whatsapp_provider() -> str:
    """
    Obtém provider ativo via env var ou settings
    
    Returns:
        Nome do provider: "legacy", "simulated", "noop", "evolution", "cloud", "baileys"
    """
    return os.getenv(
        'WHATSAPP_GATEWAY_PROVIDER',
        getattr(settings, 'WHATSAPP_GATEWAY_PROVIDER', 'legacy')
    ).lower()


def is_whatsapp_send_enabled() -> bool:
    """
    Verifica se envio está habilitado
    
    Returns:
        True se envio está habilitado
    """
    return os.getenv(
        'WHATSAPP_SEND_ENABLED',
        str(getattr(settings, 'WHATSAPP_SEND_ENABLED', True))
    ).lower() in ('true', '1', 'yes', 'on')


def is_whatsapp_shadow_mode() -> bool:
    """
    Verifica se está em modo shadow (duplica logs sem enviar)
    
    Returns:
        True se está em modo shadow
    """
    return os.getenv(
        'WHATSAPP_SHADOW_MODE',
        str(getattr(settings, 'WHATSAPP_SHADOW_MODE', False))
    ).lower() in ('true', '1', 'yes', 'on')


def get_enabled_shoppers() -> List[str]:
    """
    Obtém lista de shoppers habilitados (opcional)
    
    Returns:
        Lista de shopper_ids habilitados (vazia = todos habilitados)
    """
    # Tentar obter de env var primeiro
    shoppers_env = os.getenv('WHATSAPP_ENABLED_SHOPPERS', '')
    if shoppers_env:
        return [s.strip() for s in shoppers_env.split(',') if s.strip()]
    
    # Tentar obter de settings
    shoppers_list = getattr(settings, 'WHATSAPP_ENABLED_SHOPPERS', [])
    if isinstance(shoppers_list, list):
        return shoppers_list
    
    return []
