"""
Provider Factory - Cria instâncias de providers
"""

from typing import Dict, Optional
from .base import BaseProvider
from .chatgpt import ChatGPTProvider
from .claude import ClaudeProvider
from .image_sd import StableDiffusionProvider
from .elevenlabs import ElevenLabsProvider


class ProviderFactory:
    """Factory para criar providers"""
    
    _providers = {
        'chatgpt': ChatGPTProvider,
        'claude': ClaudeProvider,
        'stable_diffusion': StableDiffusionProvider,
        'image_sd': StableDiffusionProvider,  # Alias
        'elevenlabs': ElevenLabsProvider,
        # Adicionar mais providers conforme necessário
    }
    
    @classmethod
    def create(cls, provider_name: str, config: Optional[Dict] = None) -> BaseProvider:
        """
        Cria instância de um provider
        
        Args:
            provider_name: Nome do provider (ex: 'chatgpt')
            config: Configuração do provider
        
        Returns:
            Instância do provider
        """
        provider_class = cls._providers.get(provider_name.lower())
        
        if not provider_class:
            raise ValueError(f"Provider '{provider_name}' não encontrado")
        
        return provider_class(config)
    
    @classmethod
    def register_provider(cls, name: str, provider_class: type):
        """Registra um novo provider"""
        cls._providers[name.lower()] = provider_class
    
    @classmethod
    def list_providers(cls) -> list:
        """Lista todos os providers disponíveis"""
        return list(cls._providers.keys())

