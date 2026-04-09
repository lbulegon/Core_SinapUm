# MrFoo Food Knowledge Graph (FKG) — Integração Core_SinapUm

Subgrafo **MrFoo** no **WorldGraph (Neo4j)** do Core; sync Postgres (MrFoo) → Neo4j; insights e tools MCP.

## Pré-requisitos

- Core_SinapUm com `worldgraph_service` (Neo4j) no `docker-compose`.
- MrFoo com módulo `food_graph` e API `/api/v1/graph/...` (ver repo MrFoo).

## 1. Subir o WorldGraph (Neo4j)

```bash
cd /root/Core_SinapUm
docker compose up -d worldgraph_service
```

Portas: **7474** (HTTP), **7687** (BOLT). Servidor Core: **69.169.102.84** — para o MrFoo (ex.: Railway) conectar ao Neo4j, use `WORLDGRAPH_BOLT_URL=bolt://69.169.102.84:7687` e garanta que a porta 7687 esteja acessível. Variáveis: `WORLDGRAPH_NEO4J_USER`, `WORLDGRAPH_NEO4J_PASSWORD`.

## 2. Rodar o seed do schema MrFoo

O seed cria constraints/indexes e nós fixos de TimeSlots (ALMOCO, JANTAR, MADRUGADA). **Idempotente** (MERGE).

```bash
# Via cypher-shell no container (ajuste user/password conforme .env)
docker compose exec worldgraph_service cypher-shell -u neo4j -p <password> < services/worldgraph_service/seed/mrfoo_schema_v1.cypher
```

Ou importar manualmente o conteúdo de `services/worldgraph_service/seed/mrfoo_schema_v1.cypher` no Neo4j Browser.

## 3. Variáveis de ambiente (Core)

No Core (e onde o MCP Service roda), configurar:

- **`MRFOO_BASE_URL`**: base da API do MrFoo. **Ambiente de desenvolvimento:** `https://mrfoo-development.up.railway.app` (Railway). Produção ou local: ex. `https://mrfoo.example.com` ou `http://mrfoo:8000`.
- **`MRFOO_API_TOKEN`**: token Bearer para autenticação na API do MrFoo. Deve ser o mesmo valor configurado no MrFoo como `GRAPH_API_TOKEN` (env). O adapter envia `Authorization: Bearer <token>`.

O adapter MrFoo usa **header `X-Tenant-ID`** para contexto tenant (padrão documentado).

## 4. Seed das tools MCP mrfoo.graph.*

No Core (Django):

```bash
cd /root/Core_SinapUm
docker compose run --rm web python manage.py seed_mrfoo_graph_tools
```

Isso cria as tools: `mrfoo.graph.status`, `mrfoo.graph.sync_full`, `mrfoo.graph.sync_incremental`, `mrfoo.graph.margin_per_minute`, `mrfoo.graph.complexity_score`, `mrfoo.graph.combo_suggestions`, `mrfoo.graph.new_item_suggestions`.

## 5. Tools MCP (mrfoo.graph.*)

| Tool | Descrição | Input (ex.) |
|------|-----------|-------------|
| `mrfoo.graph.status` | Status do grafo + health Neo4j | `tenant_id` |
| `mrfoo.graph.sync_full` | Sync completo Postgres → Neo4j | `tenant_id` |
| `mrfoo.graph.sync_incremental` | Sync incremental | `tenant_id` |
| `mrfoo.graph.margin_per_minute` | Margem por minuto (timeslot opcional) | `tenant_id`, `timeslot?` |
| `mrfoo.graph.complexity_score` | Score complexidade/NOG | `tenant_id` |
| `mrfoo.graph.combo_suggestions` | Combos por co-ocorrência | `tenant_id`, `timeslot?` |
| `mrfoo.graph.new_item_suggestions` | Sugestões de novos itens | `tenant_id`, `max_items?` |

Execução: runtime `mrfoo_graph` no Core; o MCP Service delega para `POST /core/tools/<tool_name>/execute/`.

## 6. Resources sinap:// (MrFoo Graph)

Handlers delegam ao MrFooAdapter (HTTP ao MrFoo). Sempre incluir **`tenant_id`** na query.

| URI | Uso |
|-----|-----|
| `sinap://mrfoo/graph/status?tenant_id=<id>` | Status do grafo |
| `sinap://mrfoo/graph/insights/margin_per_minute?tenant_id=<id>&timeslot=JANTAR` | Margem por minuto |
| `sinap://mrfoo/graph/insights/complexity?tenant_id=<id>` | Complexidade |
| `sinap://mrfoo/graph/insights/combos?tenant_id=<id>&timeslot=ALMOCO` | Combos |
| `sinap://mrfoo/graph/insights/new_items?tenant_id=<id>&max=10` | Novos itens |

Registro: `adapters/register_resources.py` — `mrfoo` + entity `graph` (e `menu`).

## 7. Exemplos de resposta (MrFoo API)

Ao rodar os endpoints no MrFoo, você pode colar aqui as respostas reais para referência. Abaixo, exemplos esperados.

### GET /api/v1/graph/status/

**Sucesso (Neo4j conectado, já existe sync anterior):**
```json
{
  "success": true,
  "tenant_id": "1",
  "neo4j_connected": true,
  "last_synced_at": "2026-03-05T12:00:00.000000Z",
  "schema_version": "v1",
  "last_error": null
}
```

**Sucesso (Neo4j conectado, ainda sem sync):**
```json
{
  "success": true,
  "tenant_id": "1",
  "neo4j_connected": true,
  "last_synced_at": null,
  "schema_version": null,
  "last_error": null
}
```

**Erro (Neo4j inacessível ou falha):**
```json
{
  "success": false,
  "tenant_id": "1",
  "neo4j_connected": false,
  "error": "Unable to retrieve connection from pool"
}
```
*(Status HTTP: 503)*

---

### POST /api/v1/graph/sync/full/ — resultado do primeiro full sync

**Sucesso:**
```json
{
  "success": true,
  "synced": 42,
  "last_error": null
}
```

**Sucesso com aviso (ex.: algum passo ignorado por falta de dados):**
```json
{
  "success": true,
  "synced": 15,
  "last_error": null
}
```

**Falha (ex.: Empresa não encontrada ou erro no Neo4j):**
```json
{
  "success": false,
  "error": "Empresa not found",
  "synced": 0
}
```

*(Substitua os valores acima pelas respostas reais que você obteve ao testar.)*

### Como executar o teste (GET /api/v1/graph/status/)

1. Suba o MrFoo (ex.: `python manage.py runserver 8000` no repo MrFoo, com venv ativado).
2. No Core_SinapUm, rode o script (ou use curl diretamente):

```bash
# MrFoo em desenvolvimento (Railway)
curl -s "https://mrfoo-development.up.railway.app/api/v1/graph/status/" -H "X-Tenant-ID: 1"

# Usando o script (ajuste MRFOO_BASE_URL se o MrFoo estiver em outra URL/porta)
MRFOO_BASE_URL=https://mrfoo-development.up.railway.app ./scripts/test_mrfoo_graph_status.sh 1

# Local
curl -s "http://localhost:8000/api/v1/graph/status/" -H "X-Tenant-ID: 1"
```

Se o MrFoo não estiver rodando, o curl retornará falha de conexão (HTTP_CODE:000 ou connection refused).

---

## 8. Arquivos principais (Core)

- **Seed Neo4j**: `services/worldgraph_service/seed/mrfoo_schema_v1.cypher`
- **Adapter**: `adapters/mrfoo_adapter.py` (graph_status, sync, insights, get/list)
- **Runtime**: `app_mcp_tool_registry/services.py` — `_execute_runtime_mrfoo_graph`
- **MCP Service**: `services/mcp_service/main.py` — delegação `mrfoo_graph` → Core execute
- **Tools Python**: `app_mcp/tools/mrfoo/*.py`
- **Seed tools**: `app_mcp_tool_registry/management/commands/seed_mrfoo_graph_tools.py`
