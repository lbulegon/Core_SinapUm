# Instruções para Mover Evolution API

## ✅ O que já foi feito:

1. ✅ `docker-compose.yml` atualizado com caminhos relativos
2. ✅ Estrutura criada em `/root/MCP_SinapUm/services/evolution_api_service/`
3. ✅ Scripts de migração criados

## 📋 O que precisa ser feito manualmente:

### 1. Parar containers (se estiverem rodando)

```bash
cd /root/evolution_api
docker compose down
```

### 2. Mover volumes

Execute o script Python:

```bash
cd /root/MCP_SinapUm/services/evolution_api_service
python3 mover_volumes.py
```

Ou mova manualmente:

```bash
# Criar diretórios
mkdir -p /root/MCP_SinapUm/services/evolution_api_service/{pg_data,redis_data,instances,storage,mongo_data}

# Mover volumes
cp -r /root/evolution_api/pg_data/* /root/MCP_SinapUm/services/evolution_api_service/pg_data/
cp -r /root/evolution_api/redis_data/* /root/MCP_SinapUm/services/evolution_api_service/redis_data/
cp -r /root/evolution_api/instances/* /root/MCP_SinapUm/services/evolution_api_service/instances/
cp -r /root/evolution_api/storage/* /root/MCP_SinapUm/services/evolution_api_service/storage/ 2>/dev/null || true
cp -r /root/evolution_api/mongo_data/* /root/MCP_SinapUm/services/evolution_api_service/mongo_data/ 2>/dev/null || true
```

### 3. Remover pasta antiga

```bash
rm -rf /root/evolution_api
```

### 4. Subir containers no novo local

```bash
cd /root/MCP_SinapUm/services/evolution_api_service
docker compose up -d
```

## ✅ Verificação

Após mover, verifique:

```bash
# Verificar se pasta antiga foi removida
ls -la /root/ | grep evolution_api

# Verificar se volumes estão no novo local
ls -la /root/MCP_SinapUm/services/evolution_api_service/

# Verificar containers
docker ps | grep evolution
```

