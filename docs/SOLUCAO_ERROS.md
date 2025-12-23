# Solução de Erros - Portas 8005 e 8006

## 🔍 Problemas Identificados

1. **DDF (Porta 8005)** - Não está respondendo
2. **SparkScore (Porta 8006)** - Não está respondendo

## ✅ Correções Aplicadas

### 1. DDF Service

**Problemas corrigidos:**
- ✅ Conflito de porta Redis: Alterado de 6379 para 6380
- ✅ Conflito de porta PostgreSQL: Alterado de 5432 para 5434
- ✅ Arquivo .env criado

**Para subir o DDF:**
```bash
cd /root/MCP_SinapUm/services/ddf_service
docker compose down  # Parar se estiver rodando
docker compose up -d --build  # Subir novamente
```

**Verificar:**
```bash
docker logs ddf_api
curl http://localhost:8005/health
```

### 2. SparkScore Service

**Arquivos criados:**
- ✅ `docker-compose.yml` - Configuração Docker
- ✅ `Dockerfile` - Imagem Docker
- ✅ `requirements.txt` - Dependências Python
- ✅ `app/main.py` - Entrypoint FastAPI
- ✅ `app/api/routes.py` - Endpoints da API

**Para subir o SparkScore:**
```bash
cd /root/MCP_SinapUm/services/sparkscore_service
docker compose up -d --build
```

**Verificar:**
```bash
docker logs sparkscore_api
curl http://localhost:8006/health
```

## 🔧 Verificação de Conflitos de Porta

### Portas em uso:

- **5432** - PostgreSQL MCP_SinapUm
- **5433** - PostgreSQL Evolution API
- **5434** - PostgreSQL DDF ✅ (corrigido)
- **6379** - Redis Evolution API
- **6380** - Redis DDF ✅ (corrigido)
- **8004** - Evolution API ✅ (funcionando)
- **8005** - DDF ⚠️ (precisa subir)
- **8006** - SparkScore ⚠️ (precisa subir)

## 📋 Checklist de Correção

- [x] Conflitos de porta corrigidos no DDF
- [x] Arquivo .env criado para DDF
- [x] docker-compose.yml criado para SparkScore
- [x] Dockerfile criado para SparkScore
- [x] requirements.txt criado para SparkScore
- [x] API FastAPI criada para SparkScore
- [ ] DDF subido e funcionando
- [ ] SparkScore subido e funcionando

## 🚀 Próximos Passos

1. **Subir DDF:**
   ```bash
   cd /root/MCP_SinapUm/services/ddf_service
   docker compose up -d --build
   ```

2. **Subir SparkScore:**
   ```bash
   cd /root/MCP_SinapUm/services/sparkscore_service
   docker compose up -d --build
   ```

3. **Verificar ambos:**
   ```bash
   curl http://localhost:8005/health
   curl http://localhost:8006/health
   ```

