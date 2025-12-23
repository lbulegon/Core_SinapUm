"""
Configurações do OpenMind AI Server
"""
import os
from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    """Configurações da aplicação"""
    
    # API
    OPENMIND_AI_API_KEY: str = os.getenv("OPENMIND_AI_API_KEY", "om1_live_7d4102a1bf72cc497d7651beb6a98292764b1f77df947c82d086506038ea6b9921efb9d9833045d1")
    OPENMIND_AI_HOST: str = os.getenv("OPENMIND_AI_HOST", "0.0.0.0")
    OPENMIND_AI_PORT: int = int(os.getenv("OPENMIND_AI_PORT", "8000"))
    
    # IA Backend - Será um serviço separado (container Docker dedicado)
    # OPENAI_SERVICE_URL: str = os.getenv("OPENAI_SERVICE_URL", "http://openai_service:8002")
    # Por enquanto, manter compatibilidade com variáveis antigas (será removido)
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    OPENAI_MODEL: str = os.getenv("OPENAI_MODEL", "gpt-4o")
    
    # OpenMind.org Configuration (para análise de imagens)
    # URL base deve ser apenas o domínio, sem /api/core/openai
    OPENMIND_ORG_BASE_URL: str = os.getenv("OPENMIND_ORG_BASE_URL", "https://api.openmind.org/v1")
    OPENMIND_ORG_MODEL: str = os.getenv("OPENMIND_ORG_MODEL", "gpt-4o")
    
    # Ollama (opcional)
    OLLAMA_BASE_URL: str = os.getenv("OLLAMA_BASE_URL", "")
    OLLAMA_MODEL: str = os.getenv("OLLAMA_MODEL", "llama3.2-vision")
    
    # Rate Limiting
    RATE_LIMIT_PER_MINUTE: int = int(os.getenv("RATE_LIMIT_PER_MINUTE", "100"))
    RATE_LIMIT_PER_HOUR: int = int(os.getenv("RATE_LIMIT_PER_HOUR", "1000"))
    
    # Image Processing
    MAX_IMAGE_SIZE_MB: int = int(os.getenv("MAX_IMAGE_SIZE_MB", "10"))
    ALLOWED_IMAGE_FORMATS: str = os.getenv("ALLOWED_IMAGE_FORMATS", "jpeg,jpg,png,webp")
    IMAGE_MAX_DIMENSION: int = int(os.getenv("IMAGE_MAX_DIMENSION", "2048"))
    
    # Logging
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    LOG_FILE: str = os.getenv("LOG_FILE", "/var/log/openmind-ai/server.log")
    
    # CORS
    CORS_ORIGINS: str = os.getenv("CORS_ORIGINS", "*")
    
    # Security
    TOKEN_EXPIRATION: int = int(os.getenv("TOKEN_EXPIRATION", "86400"))
    
    # Media Files (Uploaded images)
    MEDIA_ROOT: str = os.getenv("MEDIA_ROOT", "/data/vitrinezap/images")
    MEDIA_URL: str = os.getenv("MEDIA_URL", "/media")
    MEDIA_HOST: str = os.getenv("MEDIA_HOST", "")
    
    # Django Évora Integration
    EVORA_API_URL: str = os.getenv("EVORA_API_URL", "http://localhost:8001")
    EVORA_API_KEY: str = os.getenv("EVORA_API_KEY", "")
    
    @property
    def allowed_formats_list(self) -> List[str]:
        """Lista de formatos permitidos"""
        return [fmt.strip().lower() for fmt in self.ALLOWED_IMAGE_FORMATS.split(",")]
    
    @property
    def max_image_size_bytes(self) -> int:
        """Tamanho máximo da imagem em bytes"""
        return self.MAX_IMAGE_SIZE_MB * 1024 * 1024
    
    @property
    def cors_origins_list(self) -> List[str]:
        """Lista de origens CORS"""
        if self.CORS_ORIGINS == "*":
            return ["*"]
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",")]
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True
        extra = "ignore"


# Instância global de configurações
settings = Settings()

