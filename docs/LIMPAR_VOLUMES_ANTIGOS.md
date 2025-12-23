# Limpar Volumes Antigos do Evolution API

## 🔍 Problema

A pasta `/root/evolution_api` ainda existe e pode estar causando confusão com os volumes do Docker. Os containers podem estar tentando usar volumes antigos.

## ✅ Solução: Limpar Tudo e Reconstruir

### 1. Parar todos os containers do Evolution

```bash
cd /root/MCP_SinapUm/services/evolution_api_service
docker compose down
```

### 2. Verificar e remover volumes órfãos do Docker

```bash
# Listar volumes relacionados ao evolution
docker volume ls | grep evolution

# Se houver volumes nomeados, removê-los
docker volume rm <nome_do_volume>
```

### 3. Verificar containers parados

```bash
# Ver todos os containers (incluindo parados)
docker ps -a | grep evolution

# Remover containers parados se necessário
docker rm <container_id>
```

### 4. Verificar bind mounts nos containers ativos

```bash
# Ver onde os volumes estão montados
docker inspect evolution_api | grep -A 10 Mounts
docker inspect postgres_evolution | grep -A 10 Mounts
docker inspect redis_evolution | grep -A 10 Mounts
```

### 5. Remover a pasta antiga completamente

```bash
# Verificar o que tem na pasta antiga
ls -lah /root/evolution_api

# Se não houver dados importantes, remover
sudo rm -rf /root/evolution_api
```

### 6. Garantir que os volumes estão no lugar certo

```bash
cd /root/MCP_SinapUm/services/evolution_api_service

# Verificar se as pastas de volumes existem
ls -lah | grep -E "pg_data|redis_data|instances"

# Se não existirem, criar (vazias)
mkdir -p pg_data redis_data instances
chmod 755 pg_data redis_data instances
```

### 7. Reconstruir os containers

```bash
cd /root/MCP_SinapUm/services/evolution_api_service

# Remover tudo e reconstruir do zero
docker compose down -v  # Remove volumes também
docker compose up -d --build
```

### 8. Verificar que está usando os caminhos corretos

```bash
# Verificar os mounts dos containers
docker inspect evolution_api --format '{{json .Mounts}}' | python3 -m json.tool
docker inspect postgres_evolution --format '{{json .Mounts}}' | python3 -m json.tool
docker inspect redis_evolution --format '{{json .Mounts}}' | python3 -m json.tool
```

**Os caminhos devem ser:**
- `/root/MCP_SinapUm/services/evolution_api_service/pg_data`
- `/root/MCP_SinapUm/services/evolution_api_service/redis_data`
- `/root/MCP_SinapUm/services/evolution_api_service/instances`

**NÃO devem ser:**
- `/root/evolution_api/*` ❌

## 🔧 Script Automatizado

Execute o script para verificar tudo:

```bash
cd /root/MCP_SinapUm/services/evolution_api_service
python3 verificar_volumes.py
```

## ⚠️ Importante

Se você já migrou os dados para `/root/MCP_SinapUm/services/evolution_api_service/`, pode remover `/root/evolution_api` com segurança:

```bash
sudo rm -rf /root/evolution_api
```

## 📝 Checklist

- [ ] Containers do Evolution parados
- [ ] Volumes órfãos do Docker removidos
- [ ] Containers antigos removidos
- [ ] Pasta `/root/evolution_api` removida
- [ ] Volumes criados em `/root/MCP_SinapUm/services/evolution_api_service/`
- [ ] Containers reconstruídos
- [ ] Verificado que os mounts estão corretos

