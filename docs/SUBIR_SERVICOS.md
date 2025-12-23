# Como Subir os Serviços - MCP SinapUm

> **💡 Arquitetura Independente**: Cada serviço é completamente isolado. Se um serviço tiver problemas, os outros continuam funcionando normalmente. Veja `ARQUITETURA_SERVICOS.md` para mais detalhes.

## 🚀 OpenMind AI (Porta 8001)

### 1. Subir OpenMind

```bash
cd /root/MCP_SinapUm/services/openmind_service
docker compose up -d --build
```

### 2. Verificar logs

```bash
docker logs openmind_service
```

### 3. Testar

```bash
# Verificar se o container está rodando
docker ps | grep openmind_service

# Testar endpoints
curl http://localhost:8001/
curl http://localhost:8001/health
curl http://localhost:8001/docs
```

### 4. Verificar volumes

Os volumes são criados automaticamente em:
- `./data/images` - Imagens processadas (mapeado para `/data/vitrinezap/images` no container)
- `./logs` - Logs do servidor

**Nota:** Este é o OpenMind AI Server (FastAPI) unificado, migrado de `/opt/openmind-ai/`.

---

## 🚀 Evolution API (Porta 8004)

### 1. Subir Evolution API

```bash
cd /root/MCP_SinapUm/services/evolution_api_service
docker compose up -d
```

### 2. Verificar logs

```bash
docker logs evolution_api
docker logs postgres_evolution
docker logs redis_evolution
```

### 3. Testar

```bash
curl http://localhost:8004
```

### 4. Verificar volumes

Os volumes são criados automaticamente em:
- `./pg_data` - Dados do PostgreSQL
- `./redis_data` - Dados do Redis
- `./instances` - Instâncias do WhatsApp

**Nota:** Se você migrou de `/root/evolution_api/`, certifique-se de que os volumes foram copiados. Veja `LIMPAR_VOLUMES_ANTIGOS.md` se houver problemas.

---

## 🚀 DDF (Porta 8005)

### 1. Criar arquivo .env

```bash
cd /root/MCP_SinapUm/services/ddf_service

# Opção 1: Usar o script Python
python3 criar_env.py

# Opção 2: Criar manualmente
cat > .env << 'EOF'
DATABASE_URL=postgresql://ddf:ddf@postgres:5432/ddf
REDIS_URL=redis://redis:6379/0
STORAGE_PATH=/app/storage
PORT=8005
EOF
```

### 2. Subir DDF

```bash
cd /root/MCP_SinapUm/services/ddf_service
docker compose down  # Parar se estiver rodando
docker compose up -d --build
```

**Nota:** O aviso sobre `version` no docker-compose.yml foi removido (está obsoleto no Docker Compose v2).

### 3. Verificar logs

```bash
docker logs ddf_api
```

### 4. Testar

```bash
curl http://localhost:8005/health
curl http://localhost:8005/ddf/categories
```

---

## 🚀 SparkScore (Porta 8006)

### 1. Subir SparkScore

```bash
cd /root/MCP_SinapUm/services/sparkscore_service
docker compose up -d --build
```

### 2. Verificar logs

```bash
docker logs sparkscore_api
```

### 3. Testar

```bash
curl http://localhost:8006/health
curl http://localhost:8006/sparkscore/orbitals
```

---

## 🔍 Verificar Todos os Serviços

```bash
# Ver containers
docker ps | grep -E "ddf|sparkscore|evolution"

# Testar HTTP
curl http://localhost:8001  # OpenMind AI
curl http://localhost:8004  # Evolution API
curl http://localhost:8005/health  # DDF
curl http://localhost:8006/health  # SparkScore
```

---

## ⚠️ Problemas Comuns

### Erro: Porta já em uso

```bash
# Verificar o que está usando a porta
sudo lsof -i :8004  # Evolution API
sudo lsof -i :8005  # DDF
sudo lsof -i :8006  # SparkScore

# Parar containers conflitantes
docker stop <container_name>
```

### Erro: Container não inicia

```bash
# Ver logs detalhados
docker logs <container_name>

# Rebuild forçado
docker compose build --no-cache
docker compose up -d
```

### Erro: Módulo não encontrado

Verificar se todos os arquivos `__init__.py` existem:
- `app/__init__.py`
- `app/core/__init__.py`
- `app/agents/__init__.py`
- `app/api/__init__.py`
- `app/motors/__init__.py`

---

## ✅ Checklist

- [ ] OpenMind: docker-compose.yml configurado
- [ ] OpenMind: Arquivo .env criado e configurado
- [ ] OpenMind: Container rodando (openmind_service)
- [ ] OpenMind: Porta 8000 respondendo
- [ ] OpenMind: Volumes criados (data/images, logs)
- [ ] Evolution API: docker-compose.yml configurado
- [ ] Evolution API: Containers rodando (evolution_api, postgres_evolution, redis_evolution)
- [ ] Evolution API: Porta 8004 respondendo
- [ ] Evolution API: Volumes criados (pg_data, redis_data, instances)
- [ ] DDF: Arquivo .env criado
- [ ] DDF: docker-compose.yml configurado
- [ ] DDF: Container rodando
- [ ] DDF: Porta 8005 respondendo
- [ ] SparkScore: docker-compose.yml criado
- [ ] SparkScore: Container rodando
- [ ] SparkScore: Porta 8006 respondendo

