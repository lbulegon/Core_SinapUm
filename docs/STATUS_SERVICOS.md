# Status dos Serviços MCP SinapUm

## ✅ Todos os Serviços Estão Rodando!

### 📦 Containers Ativos

| Serviço | Container | Porta | Status |
|---------|-----------|-------|--------|
| **Evolution API** | `evolution_api` | 8004 | ✅ Up |
| **PostgreSQL Evolution** | `postgres_evolution` | 5433 | ✅ Up |
| **Redis Evolution** | `redis_evolution` | 6379 | ✅ Up |
| **SparkScore** | `sparkscore_api` | 8006 | ✅ Up |
| **DDF** | `ddf_api` | 8005 | ✅ Up |
| **PostgreSQL DDF** | `ddf_postgres` | 5434 | ✅ Up |
| **Redis DDF** | `ddf_redis` | 6380 | ✅ Up |

## 🔍 Verificar Status

### Ver containers rodando

```bash
docker ps | grep -E "ddf|sparkscore|evolution"
```

### Testar endpoints HTTP

```bash
# Evolution API
curl http://localhost:8004

# DDF
curl http://localhost:8005/health

# SparkScore
curl http://localhost:8006/health
```

### Usar script de verificação

```bash
cd /root/MCP_SinapUm/services
python3 verificar_status.py
```

## 📊 Estrutura de Portas

```
8004 → Evolution API
8005 → DDF API
8006 → SparkScore API
5433 → PostgreSQL Evolution
5434 → PostgreSQL DDF
6379 → Redis Evolution (interno)
6380 → Redis DDF (host)
```

## 🎯 Próximos Passos

1. ✅ Todos os serviços estão rodando
2. ✅ Portas configuradas corretamente
3. ✅ Isolamento entre serviços funcionando
4. 🔄 Testar integração entre serviços
5. 🔄 Configurar monitoramento contínuo

## 📝 Comandos Úteis

### Ver logs de um serviço

```bash
docker logs evolution_api
docker logs ddf_api
docker logs sparkscore_api
```

### Reiniciar um serviço

```bash
cd /root/MCP_SinapUm/services/<service_name>
docker compose restart
```

### Parar todos os serviços

```bash
cd /root/MCP_SinapUm/services/evolution_api_service && docker compose down
cd /root/MCP_SinapUm/services/ddf_service && docker compose down
cd /root/MCP_SinapUm/services/sparkscore_service && docker compose down
```

### Subir todos os serviços

```bash
cd /root/MCP_SinapUm/services/evolution_api_service && docker compose up -d
cd /root/MCP_SinapUm/services/ddf_service && docker compose up -d
cd /root/MCP_SinapUm/services/sparkscore_service && docker compose up -d
```

---

**Última verificação:** $(date)
**Status:** ✅ Todos os serviços operacionais

