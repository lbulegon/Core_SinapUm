# Verificação de Serviços - MCP SinapUm

Guia para verificar se os serviços estão funcionando após reorganização.

## 📋 Serviços a Verificar

1. **DDF** - Porta 8005
2. **SparkScore** - Porta 8006  
3. **Evolution API** - Porta 8004

## 🔍 Verificações

### 1. Verificar Estrutura de Pastas

```bash
ls -la /root/MCP_SinapUm/services/
```

Deve mostrar:
- `ddf_service/`
- `sparkscore_service/`
- `evolution_api/`

### 2. Verificar Containers Docker

```bash
docker ps
```

Verificar se estão rodando:
- `ddf_api` (DDF)
- `evolution_api` (Evolution API)
- `postgres_evolution` (PostgreSQL Evolution)
- `redis_evolution` (Redis Evolution)

### 3. Verificar Serviços HTTP

#### DDF (Porta 8005)
```bash
curl http://localhost:8005/health
# ou
curl http://localhost:8005/
```

#### SparkScore (Porta 8006)
```bash
curl http://localhost:8006/health
# ou
curl http://localhost:8006/
```

#### Evolution API (Porta 8004)
```bash
curl http://localhost:8004
```

### 4. Verificar Docker Compose

#### DDF
```bash
cd /root/MCP_SinapUm/services/ddf_service
docker compose ps
```

#### Evolution API
```bash
cd /root/MCP_SinapUm/services/evolution_api_service
docker compose ps
```

### 5. Testar Endpoints Específicos

#### DDF - Listar Categorias
```bash
curl http://localhost:8005/ddf/categories
```

#### DDF - Detectar Tarefa
```bash
curl -X POST http://localhost:8005/ddf/detect \
  -H "Content-Type: application/json" \
  -d '{"text": "Criar uma imagem"}'
```

#### Evolution API - Health
```bash
curl http://localhost:8004/health
```

## 🚀 Script de Verificação Automática

Execute o script Python:

```bash
cd /root/MCP_SinapUm/services
python3 verificar_servicos.py
```

O script verifica:
- ✅ Estrutura de pastas
- ✅ Arquivos importantes (docker-compose.yml, etc.)
- ✅ Containers Docker
- ✅ Serviços HTTP

## ⚠️ Problemas Comuns

### Container não está rodando

```bash
# Ver logs
docker logs <container_name>

# Subir novamente
cd /root/MCP_SinapUm/services/<service>
docker compose up -d
```

### Porta já em uso

```bash
# Verificar o que está usando a porta
sudo lsof -i :8005
sudo lsof -i :8006
sudo lsof -i :8004
```

### Volumes não encontrados

Verificar se os volumes estão no local correto:
- DDF: `/root/MCP_SinapUm/services/ddf_service/`
- Evolution API: `/root/MCP_SinapUm/services/evolution_api_service/pg_data`, `redis_data`, `instances`

## ✅ Checklist Final

- [ ] Pasta `/root/evolution_api/` foi removida
- [ ] Todos os serviços estão em `/root/MCP_SinapUm/services/`
- [ ] Containers Docker estão rodando
- [ ] Serviços HTTP respondem
- [ ] Volumes estão no local correto
- [ ] docker-compose.yml está configurado corretamente

