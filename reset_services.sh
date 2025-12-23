#!/bin/bash

# Script para reset geral dos serviços do Core_SinapUm
# Uso: ./reset_services.sh [opção]
# Opções:
#   - soft: Reinicia os serviços (padrão)
#   - hard: Remove containers e recria tudo
#   - rebuild: Rebuild completo (remove containers, reconstrói imagens)

set -e

RESET_TYPE="${1:-soft}"

echo "=========================================="
echo "  RESET GERAL - Core_SinapUm"
echo "=========================================="
echo ""
echo "Tipo de reset: $RESET_TYPE"
echo ""

# Navegar para o diretório do projeto
cd "$(dirname "$0")"

case "$RESET_TYPE" in
    soft)
        echo "🔄 Reset SOFT: Reiniciando serviços..."
        docker compose restart
        ;;
    
    hard)
        echo "🔄 Reset HARD: Parando e removendo containers..."
        docker compose down
        
        echo ""
        echo "⏳ Aguardando 3 segundos..."
        sleep 3
        
        echo "▶️  Recriando containers..."
        docker compose up -d
        ;;
    
    rebuild)
        echo "🔄 Reset REBUILD: Reset completo com rebuild de imagens..."
        echo ""
        echo "⚠️  ATENÇÃO: Isso irá:"
        echo "   - Parar e remover todos os containers"
        echo "   - Reconstruir todas as imagens"
        echo "   - Recriar todos os containers"
        echo ""
        read -p "Continuar? (s/N): " -n 1 -r
        echo ""
        if [[ ! $REPLY =~ ^[Ss]$ ]]; then
            echo "❌ Operação cancelada."
            exit 1
        fi
        
        echo ""
        echo "⏹️  Parando e removendo containers..."
        docker compose down
        
        echo ""
        echo "🗑️  Removendo imagens antigas..."
        docker compose build --no-cache
        
        echo ""
        echo "⏳ Aguardando 3 segundos..."
        sleep 3
        
        echo "▶️  Criando e iniciando containers..."
        docker compose up -d
        ;;
    
    *)
        echo "❌ Opção inválida: $RESET_TYPE"
        echo ""
        echo "Uso: ./reset_services.sh [soft|hard|rebuild]"
        echo ""
        echo "Opções:"
        echo "  soft    - Reinicia os serviços (padrão)"
        echo "  hard    - Remove containers e recria tudo"
        echo "  rebuild - Reset completo com rebuild de imagens"
        exit 1
        ;;
esac

echo ""
echo "⏳ Aguardando serviços iniciarem (15 segundos)..."
sleep 15

# Mostrar status dos containers
echo ""
echo "=========================================="
echo "  Status dos Serviços"
echo "=========================================="
docker compose ps

echo ""
echo "=========================================="
echo "  Últimos logs (30 linhas)"
echo "=========================================="
docker compose logs --tail=30

echo ""
echo "✅ Reset concluído!"
echo ""
echo "Comandos úteis:"
echo "  docker compose ps          - Ver status"
echo "  docker compose logs -f     - Ver logs em tempo real"
echo "  docker compose logs web    - Ver logs do Django"
echo "  docker compose logs db     - Ver logs do PostgreSQL"
echo "  docker compose logs openmind - Ver logs do OpenMind AI"
echo ""

