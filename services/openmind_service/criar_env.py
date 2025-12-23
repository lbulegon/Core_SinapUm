#!/usr/bin/env python3
"""
Script para criar arquivo .env do OpenMind Service
"""

env_content = """# OpenMind AI Server - Variáveis de Ambiente

OPENMIND_AI_API_KEY=om1_live_7d4102a1bf72cc497d7651beb6a98292764b1f77df947c82d086506038ea6b9921efb9d9833045d1
OPENMIND_AI_HOST=0.0.0.0
OPENMIND_AI_PORT=8000

# IA Backend (OpenAI)
OPENAI_API_KEY=
OPENAI_MODEL=gpt-4o
OPENAI_BASE_URL=https://api.openai.com/v1

# Rate Limiting
RATE_LIMIT_PER_MINUTE=100
RATE_LIMIT_PER_HOUR=1000

# Image Processing
MAX_IMAGE_SIZE_MB=10
ALLOWED_IMAGE_FORMATS=jpeg,jpg,png,webp
IMAGE_MAX_DIMENSION=2048

# Logging
LOG_LEVEL=INFO
LOG_FILE=/var/log/openmind-ai/server.log

# CORS
CORS_ORIGINS=*

# Security
TOKEN_EXPIRATION=86400

# Media Files
MEDIA_ROOT=/data/vitrinezap/images
MEDIA_URL=/media
MEDIA_HOST=http://localhost:8000
"""

with open('.env', 'w') as f:
    f.write(env_content)

print("✅ Arquivo .env criado com sucesso!")

