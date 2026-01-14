#!/bin/bash

# Script para reset limpo da Evolution API
# Resolve problemas de sessão corrompida e Connection Failure do Baileys

set -e

echo "=========================================="
echo "  Reset Limpo - Evolution API (Porta 8004)"
echo "=========================================="
echo ""

BASE_URL="http://127.0.0.1:8004"
API_KEY="${EVOLUTION_API_KEY:-GKvy6psn-8HHpBQ4HAHKFOXnwjHR-oSzeGZzCaws0xg}"

HEADERS=(
    -H "Content-Type: application/json"
    -H "apikey: ${API_KEY}"
    -H "Authorization: Bearer ${API_KEY}"
)

echo "📋 Listando instâncias existentes..."
INSTANCES=$(curl -s "${HEADERS[@]}" "${BASE_URL}/instance/fetchInstances" | python3 -c "import sys, json; data=json.load(sys.stdin); print('\n'.join([i['name'] for i in data if isinstance(i, dict)]))" 2>/dev/null || echo "")

if [ -z "$INSTANCES" ]; then
    echo "   ℹ️  Nenhuma instância encontrada"
else
    echo "   Encontradas instâncias:"
    echo "$INSTANCES" | while read -r instance; do
        if [ -n "$instance" ]; then
            echo "      - $instance"
        fi
    done
fi

echo ""
echo "🗑️  Deletando todas as instâncias..."
if [ -n "$INSTANCES" ]; then
    echo "$INSTANCES" | while read -r instance; do
        if [ -n "$instance" ]; then
            echo "   Deletando: $instance"
            DELETE_RESPONSE=$(curl -s -w "\n%{http_code}" "${HEADERS[@]}" -X DELETE "${BASE_URL}/instance/delete/${instance}" 2>&1)
            HTTP_CODE=$(echo "$DELETE_RESPONSE" | tail -1)
            if [ "$HTTP_CODE" = "200" ] || [ "$HTTP_CODE" = "204" ]; then
                echo "      ✅ $instance deletada"
            else
                echo "      ⚠️  $instance - Status: $HTTP_CODE"
            fi
            sleep 1
        fi
    done
else
    echo "   ℹ️  Nenhuma instância para deletar"
fi

echo ""
echo "🔄 Reiniciando container Evolution API..."
# O docker-compose da Evolution API fica em services/evolution_api_service
cd "$(dirname "$0")/services/evolution_api_service"

# Tentar reiniciar o container (nome real: evolution-api)
if docker restart evolution-api 2>/dev/null; then
    echo "   ✅ Container 'evolution-api' reiniciado"
else
    echo "   ⚠️  Erro ao reiniciar container, tentando via docker compose..."
    if docker compose restart evolution-api 2>/dev/null; then
        echo "   ✅ Container reiniciado via docker compose"
    else
        echo "   ❌ Não foi possível reiniciar automaticamente"
        echo "   Execute manualmente:"
        echo "      docker restart evolution-api"
        echo "   ou"
        echo "      cd /root/Core_SinapUm/services/evolution_api_service && docker compose restart evolution-api"
    fi
fi

echo ""
echo "⏳ Aguardando serviço ficar disponível (15 segundos)..."
sleep 15

echo ""
echo "🔍 Verificando status do serviço..."
HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" --connect-timeout 5 "${BASE_URL}/" 2>&1 || echo "000")

if [ "$HTTP_CODE" = "200" ]; then
    echo "   ✅ Serviço Evolution API está respondendo (HTTP $HTTP_CODE)"
else
    echo "   ⚠️  Serviço pode não estar respondendo (HTTP $HTTP_CODE)"
    echo "   Aguarde mais alguns segundos e verifique os logs:"
    echo "      docker logs evolution_api --tail 50"
fi

echo ""
echo "=========================================="
echo "  Reset Concluído"
echo "=========================================="
echo ""
echo "Próximos passos:"
echo "1. Acesse o dashboard do Django e crie uma nova conexão WhatsApp"
echo "2. O sistema irá criar uma nova instância 'default' automaticamente"
echo "3. Escaneie o QR Code gerado"
echo ""
echo "Para ver logs em tempo real:"
echo "   docker logs -f evolution_api"
echo ""

