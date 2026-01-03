"""
Configurações do serviço ifood_service
"""
import os
from typing import Optional


class Settings:
    """Configurações do serviço"""
    
    def __init__(self):
        # OAuth iFood
        self.IFOOD_CLIENT_ID = os.getenv("IFOOD_CLIENT_ID", "")
        self.IFOOD_CLIENT_SECRET = os.getenv("IFOOD_CLIENT_SECRET", "")
        self.IFOOD_AUTH_BASE_URL = os.getenv("IFOOD_AUTH_BASE_URL", "https://auth.ifood.com.br")
        self.IFOOD_API_BASE_URL = os.getenv("IFOOD_API_BASE_URL", "https://merchant-api.ifood.com.br")
        self.IFOOD_REDIRECT_URI = os.getenv("IFOOD_REDIRECT_URI", "http://localhost:7020/oauth/callback")
        
        # Core SinapUm
        self.CORE_INTERNAL_BASE_URL = os.getenv("CORE_INTERNAL_BASE_URL", "http://web:5000")
        self.INTERNAL_API_KEY = os.getenv("INTERNAL_API_KEY", "")
        
        # Redis (opcional)
        self.REDIS_URL = os.getenv("REDIS_URL", "")
        
        # Validação básica
        if not self.IFOOD_CLIENT_ID:
            raise ValueError("IFOOD_CLIENT_ID environment variable is required")
        if not self.IFOOD_CLIENT_SECRET:
            raise ValueError("IFOOD_CLIENT_SECRET environment variable is required")
        if not self.INTERNAL_API_KEY:
            raise ValueError("INTERNAL_API_KEY environment variable is required")
