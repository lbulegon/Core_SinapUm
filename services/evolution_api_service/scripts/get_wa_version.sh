#!/bin/bash
# Script para obter a versão atual do WhatsApp Web
# Uso: ./scripts/get_wa_version.sh
#      ou: bash scripts/get_wa_version.sh

set -e

WA_CHECK_URL="https://web.whatsapp.com/check-update?version=0&platform=web"

echo "🔍 Consultando versão atual do WhatsApp Web..."
echo ""

# Faz a requisição e extrai a versão
RESPONSE=$(curl -s "$WA_CHECK_URL" || echo "")

if [ -z "$RESPONSE" ]; then
    echo "❌ Erro: Não foi possível conectar ao endpoint do WhatsApp Web"
    echo "   URL: $WA_CHECK_URL"
    exit 1
fi

# Extrai a versão usando jq (se disponível) ou grep/sed
if command -v jq &> /dev/null; then
    VERSION=$(echo "$RESPONSE" | jq -r '.currentVersion // empty')
else
    VERSION=$(echo "$RESPONSE" | grep -o '"currentVersion":"[^"]*"' | cut -d'"' -f4)
fi

if [ -z "$VERSION" ]; then
    echo "❌ Erro: Não foi possível extrair a versão da resposta"
    echo "   Resposta recebida: $RESPONSE"
    exit 1
fi

echo "✅ Versão atual do WhatsApp Web: $VERSION"
echo ""
echo "📋 Para atualizar no docker-compose.yml, altere:"
echo "   CONFIG_SESSION_PHONE_VERSION: $VERSION"
echo ""
echo "💡 Comando one-liner para atualizar:"
echo "   sed -i 's/CONFIG_SESSION_PHONE_VERSION:.*/CONFIG_SESSION_PHONE_VERSION: $VERSION/' docker-compose.yml"
echo ""

# Retorna a versão para uso em scripts
echo "$VERSION"
