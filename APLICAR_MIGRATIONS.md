# Aplicar Migrations do app_mcp_tool_registry

## Passos para aplicar as migrations

### 1. Dentro do container Docker

```bash
# Entrar no container do Django
docker exec -it mcp_sinapum_web bash

# Criar migrations
python manage.py makemigrations app_mcp_tool_registry

# Aplicar migrations
python manage.py migrate app_mcp_tool_registry

# Popular dados iniciais
python manage.py seed_mcp_registry
```

### 2. Ou via docker-compose

```bash
cd /root/Core_SinapUm

# Criar migrations
docker compose exec web python manage.py makemigrations app_mcp_tool_registry

# Aplicar migrations
docker compose exec web python manage.py migrate app_mcp_tool_registry

# Popular dados iniciais
docker compose exec web python manage.py seed_mcp_registry
```

## O que será criado

### Tabelas no banco:
- `mcp_client_app` - Aplicações clientes
- `mcp_tool` - Tools disponíveis
- `mcp_tool_version` - Versões das tools
- `mcp_tool_call_log` - Logs de chamadas

### Dados iniciais (seed):
- ClientApp: `vitrinezap` com API key gerada
- Tool: `vitrinezap.analisar_produto`
- ToolVersion: `1.0.0` com schemas e config

## Endpoints disponíveis

Após aplicar as migrations, os seguintes endpoints estarão disponíveis:

- `GET /core/tools/` - Lista todas as tools
- `GET /core/tools/<tool_name>/` - Detalhes de uma tool
- `POST /core/tools/resolve/` - Resolve uma tool
- `POST /core/tools/log/` - Registra log de chamada

## Autenticação

Os endpoints POST requerem header:
```
X-SINAPUM-KEY: <api_key>
```

A API key será exibida após executar `seed_mcp_registry`.

