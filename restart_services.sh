#!/bin/bash

# Script para reiniciar todos os serviços do Core_SinapUm
# Uso: ./restart_services.sh

set -e

echo "=========================================="
echo "  Reiniciando serviços Core_SinapUm"
echo "=========================================="
echo ""

# Navegar para o diretório do projeto
cd "$(dirname "$0")"

echo "🔄 Reiniciando todos os serviços..."
docker compose restart

echo ""
echo "⏳ Aguardando serviços reiniciarem (10 segundos)..."
sleep 10

# Mostrar status dos containers
echo ""
echo "=========================================="
echo "  Status dos Serviços"
echo "=========================================="
docker compose ps

echo ""
echo "=========================================="
echo "  Últimos logs (20 linhas)"
echo "=========================================="
docker compose logs --tail=20

echo ""
echo "✅ Reinicialização concluída!"
echo ""
echo "Para ver os logs em tempo real, use:"
echo "  docker compose logs -f"
echo ""
echo "Para um reset mais completo, use:"
echo "  ./reset_services.sh hard"

