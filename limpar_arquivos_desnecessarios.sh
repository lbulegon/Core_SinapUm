#!/bin/bash
# Script para limpar arquivos desnecessários do repositório
# Remove arquivos que não devem estar no Git

echo "🧹 Limpando arquivos desnecessários..."

# Remover arquivos Python compilados
find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null
find . -name "*.pyc" -delete 2>/dev/null
find . -name "*.pyo" -delete 2>/dev/null
find . -name "*.pyd" -delete 2>/dev/null

# Remover arquivos de log
find . -name "*.log" -not -path "./.git/*" -delete 2>/dev/null
find . -name "*.log.*" -not -path "./.git/*" -delete 2>/dev/null

# Remover dados de runtime dos serviços Docker
rm -rf services/*/pg_data/* 2>/dev/null
rm -rf services/*/mongo_data/* 2>/dev/null
rm -rf services/*/redis_data/* 2>/dev/null

# Remover arquivos temporários
find . -name "*.tmp" -not -path "./.git/*" -delete 2>/dev/null
find . -name "*.temp" -not -path "./.git/*" -delete 2>/dev/null
find . -name "*.bak" -not -path "./.git/*" -delete 2>/dev/null
find . -name "*.backup" -not -path "./.git/*" -delete 2>/dev/null

# Remover arquivos de cache
find . -name ".cache" -type d -exec rm -rf {} + 2>/dev/null
find . -name ".pytest_cache" -type d -exec rm -rf {} + 2>/dev/null
find . -name ".mypy_cache" -type d -exec rm -rf {} + 2>/dev/null

# Remover arquivos de IDE
find . -name ".vscode" -type d -exec rm -rf {} + 2>/dev/null
find . -name ".idea" -type d -exec rm -rf {} + 2>/dev/null
find . -name "*.swp" -delete 2>/dev/null
find . -name "*.swo" -delete 2>/dev/null
find . -name "*~" -delete 2>/dev/null

# Remover arquivos do sistema
find . -name ".DS_Store" -delete 2>/dev/null
find . -name "Thumbs.db" -delete 2>/dev/null

# Remover staticfiles gerados (serão regenerados)
# CUIDADO: Só remover se não houver mudanças importantes
# rm -rf staticfiles/* 2>/dev/null

echo "✅ Limpeza concluída!"
echo ""
echo "📊 Status do repositório:"
git status --short | wc -l | xargs echo "Arquivos modificados/não rastreados:"

