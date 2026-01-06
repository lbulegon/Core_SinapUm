"""
Router singleton que retorna provider ativo
"""
import os
from typing import Optional
from django.conf import settings
from app_whatsapp.domain.provider_contract import IWhatsAppProvider
from app_whatsapp.providers.provider_simulated import ProviderSimulated
from app_whatsapp.providers.provider_cloud import ProviderCloud
from app_whatsapp.providers.provider_baileys import ProviderBaileys
from app_whatsapp.providers.provider_evolution import ProviderEvolution


class WhatsAppRouter:
    """Router singleton que retorna provider ativo"""
    
    _instance: Optional['WhatsAppRouter'] = None
    _provider: Optional[IWhatsAppProvider] = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def get_provider(self) -> IWhatsAppProvider:
        """
        Retorna provider ativo baseado em WHATSAPP_PROVIDER
        
        Returns:
            Instância do provider ativo
        """
        if self._provider is None:
            provider_name = os.getenv(
                'WHATSAPP_PROVIDER',
                getattr(settings, 'WHATSAPP_PROVIDER', 'simulated')
            ).lower()
            
            if provider_name == 'simulated':
                self._provider = ProviderSimulated()
            elif provider_name == 'cloud':
                self._provider = ProviderCloud()
            elif provider_name == 'baileys':
                self._provider = ProviderBaileys()
            elif provider_name == 'evolution':
                self._provider = ProviderEvolution()
            else:
                raise ValueError(f"Unknown provider: {provider_name}")
        
        return self._provider
