"""
Configurações do Baileys Service
================================
"""
import os
from pathlib import Path
from django.conf import settings

# Diretório base para sessões
BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent
SESSIONS_DIR = Path(getattr(settings, 'BAILEYS_SESSIONS_DIR', BASE_DIR / 'sessions' / 'baileys'))
SESSIONS_DIR.mkdir(parents=True, exist_ok=True)

# Configurações de conexão
RECONNECT_DELAY = int(os.getenv('BAILEYS_RECONNECT_DELAY', '5'))  # segundos
MAX_RECONNECT_ATTEMPTS = int(os.getenv('BAILEYS_MAX_RECONNECT_ATTEMPTS', '10'))
CONNECTION_TIMEOUT = int(os.getenv('BAILEYS_CONNECTION_TIMEOUT', '30'))  # segundos

# Configurações de mensagens
MESSAGE_TIMEOUT = int(os.getenv('BAILEYS_MESSAGE_TIMEOUT', '30000'))  # milissegundos
ENABLE_HIGH_QUALITY_LINK_PREVIEW = os.getenv('BAILEYS_HIGH_QUALITY_PREVIEW', 'true').lower() == 'true'

# Logging
LOG_LEVEL = os.getenv('BAILEYS_LOG_LEVEL', 'INFO')
FILTER_LOGS = os.getenv('BAILEYS_FILTER_LOGS', 'true').lower() == 'true'

# Media
MEDIA_DIR = Path(getattr(settings, 'BAILEYS_MEDIA_DIR', BASE_DIR / 'media' / 'baileys'))
MEDIA_DIR.mkdir(parents=True, exist_ok=True)
