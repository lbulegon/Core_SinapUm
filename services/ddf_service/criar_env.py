#!/usr/bin/env python3
"""
Script para criar arquivo .env do DDF
"""

env_content = """DATABASE_URL=postgresql://ddf:ddf@postgres:5432/ddf
REDIS_URL=redis://redis:6379/0
STORAGE_PATH=/app/storage
PORT=8005
"""

with open('.env', 'w') as f:
    f.write(env_content)

print("✅ Arquivo .env criado com sucesso!")

