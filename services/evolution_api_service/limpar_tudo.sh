#!/bin/bash
# Script para limpar completamente e reconstruir o Evolution API

set -e

echo "🧹 Limpando Evolution API..."
echo ""

# 1. Parar containers
echo "1️⃣  Parando containers..."
cd /root/MCP_SinapUm/services/evolution_api
docker compose down

# 2. Remover containers parados
echo ""
echo "2️⃣  Removendo containers parados..."
docker ps -a | grep evolution | awk '{print $1}' | xargs -r docker rm -f

# 3. Listar volumes órfãos
echo ""
echo "3️⃣  Verificando volumes órfãos..."
VOLUMES=$(docker volume ls | grep evolution | awk '{print $2}')
if [ -n "$VOLUMES" ]; then
    echo "   Volumes encontrados:"
    echo "$VOLUMES"
    read -p "   Remover estes volumes? (s/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Ss]$ ]]; then
        echo "$VOLUMES" | xargs -r docker volume rm
    fi
else
    echo "   ✅ Nenhum volume órfão encontrado"
fi

# 4. Verificar pasta antiga
echo ""
echo "4️⃣  Verificando pasta /root/evolution_api..."
if [ -d "/root/evolution_api" ]; then
    echo "   ⚠️  Pasta antiga ainda existe!"
    ls -lah /root/evolution_api
    read -p "   Remover pasta /root/evolution_api? (s/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Ss]$ ]]; then
        sudo rm -rf /root/evolution_api
        echo "   ✅ Pasta removida"
    fi
else
    echo "   ✅ Pasta antiga não existe"
fi

# 5. Garantir que os volumes estão no lugar certo
echo ""
echo "5️⃣  Criando diretórios de volumes..."
cd /root/MCP_SinapUm/services/evolution_api
mkdir -p pg_data redis_data instances
chmod 755 pg_data redis_data instances
echo "   ✅ Diretórios criados"

# 6. Reconstruir
echo ""
echo "6️⃣  Reconstruindo containers..."
docker compose up -d --build

# 7. Verificar mounts
echo ""
echo "7️⃣  Verificando mounts dos containers..."
echo ""
echo "📋 Evolution API:"
docker inspect evolution_api --format '{{range .Mounts}}{{.Source}} -> {{.Destination}}{{"\n"}}{{end}}' | grep -v "^$" || echo "   Container não está rodando"

echo ""
echo "📋 PostgreSQL:"
docker inspect postgres_evolution --format '{{range .Mounts}}{{.Source}} -> {{.Destination}}{{"\n"}}{{end}}' | grep -v "^$" || echo "   Container não está rodando"

echo ""
echo "📋 Redis:"
docker inspect redis_evolution --format '{{range .Mounts}}{{.Source}} -> {{.Destination}}{{"\n"}}{{end}}' | grep -v "^$" || echo "   Container não está rodando"

echo ""
echo "✅ Limpeza concluída!"
echo ""
echo "💡 Para verificar logs:"
echo "   docker logs evolution_api"
echo "   docker logs postgres_evolution"
echo "   docker logs redis_evolution"

