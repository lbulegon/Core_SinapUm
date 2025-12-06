#!/bin/bash
# Script para configurar o Git

echo "🔧 Configurando Git..."

# Solicitar nome e email
echo ""
echo "Por favor, forneça suas informações do Git:"
echo ""

read -p "Nome completo: " GIT_NAME
read -p "Email do GitHub: " GIT_EMAIL

# Configurar Git
if [ -n "$GIT_NAME" ] && [ -n "$GIT_EMAIL" ]; then
    git config --global user.name "$GIT_NAME"
    git config --global user.email "$GIT_EMAIL"
    
    echo ""
    echo "✅ Git configurado com sucesso!"
    echo ""
    echo "Nome: $(git config --global user.name)"
    echo "Email: $(git config --global user.email)"
    echo ""
    echo "Agora você pode fazer commits normalmente."
else
    echo "❌ Erro: Nome e email são obrigatórios"
    exit 1
fi

