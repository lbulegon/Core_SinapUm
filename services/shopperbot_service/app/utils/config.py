"""Configurações do serviço"""
import os
from pathlib import Path
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Configurações da aplicação"""
    
    # Servidor
    PORT: int = int(os.getenv("PORT", "7030"))
    DEBUG: bool = os.getenv("DEBUG", "False").lower() == "true"
    
    # Storage
    STORAGE_PATH: Path = Path(os.getenv("STORAGE_PATH", "./storage"))
    CARDS_PATH: Path = STORAGE_PATH / "cards"
    
    # Database
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        "postgresql://sinapum:sinapum123@postgres:5432/sinapum"
    )
    
    # MCP Core (VitrineZap tools: cart, catalog, order)
    MCP_CORE_URL: str = os.getenv(
        "MCP_CORE_URL",
        "http://web:5000"
    )
    MCP_ENABLED: bool = os.getenv("MCP_ENABLED", "true").lower() in ("1", "true", "yes")
    
    # Logging
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()

# Exportar constantes para uso fácil
PORT = settings.PORT
DEBUG = settings.DEBUG
STORAGE_PATH = settings.STORAGE_PATH
CARDS_PATH = settings.CARDS_PATH
DATABASE_URL = settings.DATABASE_URL
LOG_LEVEL = settings.LOG_LEVEL
