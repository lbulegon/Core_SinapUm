#!/bin/bash
# Script para mover volumes do Evolution API

echo "Movendo volumes do Evolution API..."

# Criar diretórios se não existirem
mkdir -p /root/MCP_SinapUm/services/evolution_api/{pg_data,redis_data,instances,storage,mongo_data}

# Mover volumes (se existirem)
if [ -d "/root/evolution_api/pg_data" ]; then
    echo "Movendo pg_data..."
    cp -r /root/evolution_api/pg_data/* /root/MCP_SinapUm/services/evolution_api/pg_data/ 2>/dev/null
fi

if [ -d "/root/evolution_api/redis_data" ]; then
    echo "Movendo redis_data..."
    cp -r /root/evolution_api/redis_data/* /root/MCP_SinapUm/services/evolution_api/redis_data/ 2>/dev/null
fi

if [ -d "/root/evolution_api/instances" ]; then
    echo "Movendo instances..."
    cp -r /root/evolution_api/instances/* /root/MCP_SinapUm/services/evolution_api/instances/ 2>/dev/null
fi

if [ -d "/root/evolution_api/storage" ]; then
    echo "Movendo storage..."
    cp -r /root/evolution_api/storage/* /root/MCP_SinapUm/services/evolution_api/storage/ 2>/dev/null
fi

if [ -d "/root/evolution_api/mongo_data" ]; then
    echo "Movendo mongo_data..."
    cp -r /root/evolution_api/mongo_data/* /root/MCP_SinapUm/services/evolution_api/mongo_data/ 2>/dev/null
fi

echo "Volumes movidos. Agora você pode remover /root/evolution_api/"

