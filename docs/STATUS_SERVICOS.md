# 📊 Status dos Serviços - Core_SinapUm

## ✅ Serviços Rodando

1. **mcp_sinapum_db** (PostgreSQL)
   - Status: Up 19 minutes (healthy)
   - Porta: 5432

2. **openmind_service** (OpenMind AI)
   - Status: Up 2 hours (healthy)
   - Porta: 8001

## ⚠️ Serviços Criados mas Não Rodando

1. **mcp_sinapum_web** (Django Core Registry)
   - Status: Created (não iniciado)
   - Ação: Precisa iniciar

2. **mcp_sinapum_openmind** (OpenMind do Core)
   - Status: Created (não iniciado)
   - Ação: Precisa iniciar

3. **mcp_sinapum_mcp_service** (MCP Service)
   - Status: Created (não iniciado)
   - Ação: Precisa iniciar

## ❌ Serviços Não Encontrados

1. **evolution_api** (Evolution API Service)
   - Status: Container não existe
   - Ação: Precisa subir

2. **ddf_api** (DDF Service)
   - Status: Container não existe
   - Ação: Precisa subir

3. **sparkscore_api** (SparkScore Service)
   - Status: Container não existe
   - Ação: Precisa subir

## 🚀 Como Subir Todos os Serviços

### 1. Core_SinapUm (Django + DB + OpenMind)
```bash
cd /root/Core_SinapUm
docker compose up -d
```

### 2. Serviços Individuais

```bash
# Evolution API
cd /root/Core_SinapUm/services/evolution_api_service
docker compose up -d

# DDF Service
cd /root/Core_SinapUm/services/ddf_service
docker compose up -d

# SparkScore Service
cd /root/Core_SinapUm/services/sparkscore_service
docker compose up -d

# MCP Service
cd /root/Core_SinapUm/services/mcp_service
docker compose up -d
```

### 3. Ou usar o script principal
```bash
cd /root
./restart_all_services.sh
```

## 📋 Resumo

- **Rodando**: 2 serviços (db, openmind_service)
- **Criados mas parados**: 3 serviços (web, openmind, mcp_service)
- **Não existem**: 3 serviços (evolution_api, ddf_api, sparkscore_api)

**Total esperado**: 8 serviços
**Total rodando**: 2 serviços
**Ação necessária**: Subir 6 serviços

