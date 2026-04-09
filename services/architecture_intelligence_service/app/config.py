"""
Configurações do Architecture Intelligence Service.

ADAPTAR: Segue padrão pydantic_settings do ShopperBot/OpenMind.
Para usar BaseSettings, adicione pydantic-settings ao requirements.
"""
import os
from pathlib import Path


class Settings:
    """Configurações da aplicação (carregadas de env)"""

    # Servidor
    PORT: int = int(os.getenv("ARCHITECTURE_INTELLIGENCE_PORT", "7025"))
    DEBUG: bool = os.getenv("DEBUG", "False").lower() == "true"

    # LLM / OpenMind
    OPENMIND_SERVICE_URL: str = os.getenv("OPENMIND_SERVICE_URL", "http://openmind:8001")
    OPENMIND_AI_KEY: str = os.getenv("OPENMIND_AI_KEY", "")
    LLM_PROVIDER: str = os.getenv("AIS_LLM_PROVIDER", "openmind")

    # Prompts
    PROMPTS_DIR: Path = Path("app/prompts")

    # Storage - ADAPTAR: PostgreSQL quando integrar ao Core
    STORAGE_BACKEND: str = os.getenv("AIS_STORAGE_BACKEND", "memory")

    # Logging
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")


settings = Settings()
