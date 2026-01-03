#!/bin/bash

# Script para iniciar o serviço Evolution API
# Uso: ./start_evolution.sh

set -e

echo "=========================================="
echo "  Iniciando Evolution API (Porta 8004)"
echo "=========================================="
echo ""

# Navegar para o diretório do projeto
cd "$(dirname "$0")"

# Verificar se docker compose está disponível
if ! command -v docker &> /dev/null; then
    echo "❌ Docker não está instalado ou não está no PATH"
    exit 1
fi

# Verificar se o arquivo docker-compose.yml existe
if [ ! -f "docker-compose.yml" ]; then
    echo "❌ Arquivo docker-compose.yml não encontrado"
    exit 1
fi

echo "🚀 Iniciando containers Evolution API..."
docker compose up -d evolution_api postgres_evolution redis_evolution

echo ""
echo "⏳ Aguardando serviços iniciarem (10 segundos)..."
sleep 10

# Verificar status
echo ""
echo "=========================================="
echo "  Status dos Containers"
echo "=========================================="
docker compose ps evolution_api postgres_evolution redis_evolution

echo ""
echo "🔍 Verificando se o serviço está respondendo..."
sleep 5

HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" --connect-timeout 5 http://127.0.0.1:8004/ 2>&1 || echo "000")

if [ "$HTTP_CODE" = "200" ]; then
    echo "   ✅ Serviço Evolution API está respondendo (HTTP $HTTP_CODE)"
    echo ""
    echo "   URL: http://69.169.102.84:8004"
    echo "   Status: ONLINE"
else
    echo "   ⚠️  Serviço pode não estar respondendo ainda (HTTP $HTTP_CODE)"
    echo "   Aguarde mais alguns segundos e verifique os logs:"
    echo "      docker logs evolution_api --tail 50"
fi

echo ""
echo "=========================================="
echo "  Comandos Úteis"
echo "=========================================="
echo ""
echo "Ver logs em tempo real:"
echo "   docker logs -f evolution_api"
echo ""
echo "Parar o serviço:"
echo "   docker compose stop evolution_api"
echo ""
echo "Reiniciar o serviço:"
echo "   docker compose restart evolution_api"
echo ""
echo "Ver status:"
echo "   docker compose ps evolution_api"
echo ""
echo "Reset completo (deleta instâncias e reinicia):"
echo "   ./reset_evolution.sh"
echo ""

