# Plano de Execução: MCP + ACP + A2A — Core_SinapUm

**Missão:** Evoluir o Core_SinapUm para arquitetura explícita MCP + ACP + A2A **sem quebrar** funcionalidades existentes. Tudo aditivo: wrappers, adapters, novos módulos, feature flags, dual-run.

---

## A) Plano de Execução (PRs)

| PR | Fase | Conteúdo | Arquivos principais |
|----|------|----------|----------------------|
| **PR1** | 0 | Inventário + doc | Este doc, confirmação de árvore |
| **PR2** | 1a | MCP Resources: parser `sinap://`, resolver, schema | `mcp/uri.py`, `mcp/resources/`, `app_mcp_tool_registry` ou `services/mcp_service` |
| **PR3** | 1b | Prompts versionados: convenção `{vertical}/{purpose}/v{N}`, resolver compatível | `app_mcp_tool_registry/utils.py`, `app_sinapum` (sem mudar contrato) |
| **PR4** | 1c | ToolCallLog: campos tokens/custo (nullable) | `app_mcp_tool_registry/models.py`, migration |
| **PR5** | 2a | ACP: modelo `AgentTask` + migrations | `app_acp/` (novo app), `models.py` — ✅ |
| **PR6** | 2b | ACP: TaskManager, ExecutionEngine, StateStore, Celery | `app_acp/task_manager.py`, `execution_engine.py`, `state_store.py`, tasks — ✅ |
| **PR7** | 2c | ACP: API Django `/acp/tasks/` | `app_acp/views.py`, `urls.py`, `setup/urls.py` — ✅ |
| **PR8** | 3a | A2A: PlannerAgent + ExecutorAgent (mínimo) | `a2a/planner_agent.py`, `a2a/executor_agent.py` |
| **PR9** | 3b | A2A: endpoint `POST /a2a/run` ou `POST /agent/run` | `a2a/views.py`, rotas, integração ACP |
| **PR10** | 4a | Adapters: pasta `adapters/`, vitrinezap, motopro, mrfoo, openmind, ifood, ddf | `adapters/*.py` |
| **PR11** | 4b | Feature flags ACP_ENABLED, MCP_RESOURCES_ENABLED; dual-run opcional | `core/services/feature_flags`, uso em flow |
| **PR12** | 5 | Hardening: timeouts, retries, idempotência por tool, testes e READMEs | Vários |

---

## B) Estrutura de pastas (apenas o que será criado)

```
Core_SinapUm/
├── mcp/                          # NOVO: convenção/referência (não substitui app_mcp*)
│   ├── README.md
│   ├── uri.py                    # Parser sinap://
│   ├── resources/                # Resolver de resources
│   │   ├── __init__.py
│   │   ├── resolver.py
│   │   └── schemas.py
│   └── utils/
│       └── telemetry.py          # Formato comum de log (opcional, pode ficar em core/services)
│
├── app_acp/                      # NOVO: Django app ACP
│   ├── __init__.py
│   ├── apps.py
│   ├── models.py                 # AgentTask
│   ├── task_manager.py
│   ├── execution_engine.py
│   ├── state_store.py
│   ├── views.py
│   ├── urls.py
│   ├── admin.py
│   ├── migrations/
│   └── README.md
│
├── a2a/                          # NOVO: módulo Python (ou app Django se preferir)
│   ├── __init__.py
│   ├── planner_agent.py
│   ├── executor_agent.py
│   ├── schemas.py                # A2A plan (steps)
│   └── README.md
│
├── adapters/                     # NOVO: camada adapter por vertical
│   ├── __init__.py
│   ├── base.py                   # Interface base
│   ├── vitrinezap_adapter.py
│   ├── motopro_adapter.py
│   ├── mrfoo_adapter.py
│   ├── openmind_adapter.py
│   ├── ifood_adapter.py
│   └── ddf_adapter.py
│
├── app_mcp_tool_registry/        # EXISTENTE — alterações aditivas
│   ├── models.py                 # + ToolCallLog: tokens_in, tokens_out, cost_usd, model, provider (nullable)
│   └── ...
│
├── services/mcp_service/         # EXISTENTE — alterações aditivas
│   └── main.py                   # + rotas /mcp/resources/... (get, list) se exposto aqui
│
├── core/services/
│   └── telemetry.py              # NOVO (ou estender existente): formato padrão de log
│
└── setup/
    └── urls.py                   # + path('acp/', include('app_acp.urls')), path('a2a/', ...) ou agent/run
```

**Não mover:** `app_mcp`, `app_mcp_tool_registry`, `app_sinapum`, `services/mcp_service` — apenas adicionar e referenciar.

---

## C) Contratos (schemas) essenciais

### 1) URI `sinap://`

```
sinap://{vertical}/{entity}/{id}
sinap://{vertical}/{entity}?query...
```

- **vertical:** vitrinezap | motopro | mrfoo | system
- **entity:** catalog | orders | menu | tools | logs | ...
- **id:** opcional (para get por id)
- **query:** opcional (list/search)

Exemplos:
- `sinap://vitrinezap/catalog/123`
- `sinap://motopro/orders/987`
- `sinap://mrfoo/menu/2026-W09`
- `sinap://system/tools`

### 2) AgentTask (Postgres)

```json
{
  "task_id": "uuid",
  "agent_name": "string",
  "status": "PENDING|RUNNING|WAITING|FAILED|COMPLETED|CANCELLED",
  "payload": {},
  "result": {} | null,
  "error": "string" | null,
  "trace_id": "string" | null,
  "retry_count": 0,
  "max_retries": 3,
  "timeout_seconds": 120 | null,
  "created_at": "iso8601",
  "updated_at": "iso8601",
  "started_at": "iso8601" | null,
  "finished_at": "iso8601" | null,
  "idempotency_key": "string" | null
}
```

### 3) A2A Plan (steps)

```json
{
  "plan_id": "uuid",
  "trace_id": "string",
  "steps": [
    {
      "step_id": "string",
      "tool": "vitrinezap.catalog.get",
      "version": "1.0",
      "input": {},
      "depends_on": []
    }
  ],
  "context": {}
}
```

---

## D) Lista de arquivos a criar/alterar

| Ação | Caminho |
|------|---------|
| CREATE | `mcp/README.md` |
| CREATE | `mcp/uri.py` |
| CREATE | `mcp/resources/__init__.py` |
| CREATE | `mcp/resources/resolver.py` |
| CREATE | `mcp/resources/schemas.py` |
| CREATE | `app_acp/` (app completo) |
| CREATE | `a2a/__init__.py`, `planner_agent.py`, `executor_agent.py`, `schemas.py`, `README.md` |
| CREATE | `adapters/__init__.py`, `base.py`, `vitrinezap_adapter.py`, ... |
| CREATE | `core/services/telemetry.py` (se não existir) |
| MODIFY | `app_mcp_tool_registry/models.py` (ToolCallLog: tokens_in, tokens_out, cost_usd, model, provider — nullable) |
| MODIFY | `app_mcp_tool_registry/utils.py` (resolver prompt ref convenção `vertical/purpose/vN`) |
| MODIFY | `services/mcp_service/main.py` (rotas resources GET/LIST opcional) |
| MODIFY | `setup/settings.py` (INSTALLED_APPS += app_acp) |
| MODIFY | `setup/urls.py` (acp/, a2a/ ou agent/run) |

---

## E) Notas de compatibilidade

- **Legado:** Nenhum endpoint existente alterado. `/core/tools/resolve/`, `/core/tools/log/`, `/mcp/call` mantêm contrato. Novos campos em `ToolCallLog` são nullable.
- **Context Pack:** Continua opcional; `trace_id` continua nullable.
- **Prompts:** Resolver aceita refs antigas (`analise_produto_imagem_v1`, `sistema:nome`) e nova convenção (`vitrinezap/followup/v1`) sem migração destrutiva.
- **ACP/A2A:** Novas rotas namespaced (`/acp/*`, `/a2a/*`). Fluxo legado (ex.: `task_queue_service/flow.py`) não é alterado; dual-run pode chamar ambos e comparar.
- **Adapters:** Tools MCP passam a chamar adapters; implementação atual em `app_mcp/clients` e serviços pode ser encapsulada nos adapters sem remover código antigo.

---

## Inventário confirmado (Fase 0)

- **Apps Django:** app_sinapum, app_mcp_tool_registry, app_mcp, app_inbound_events, app_creative_engine, app_leads, app_whatsapp_gateway, app_whatsapp, app_conversations, app_ai_bridge, app_whatsapp_events, core.services.whatsapp, core.services.feature_flags.
- **Rotas MCP:** `/core/tools/` (list, resolve, log, get_tool_detail, execute_tool_view), `/mcp/tools` (list), `POST /mcp/call`.
- **Models MCP:** Tool, ToolVersion, ToolCallLog, ClientApp em `app_mcp_tool_registry.models`.
- **Tools atuais:** catalog_search, product_get, cart_get, cart_add, order_create, order_status em `app_mcp/tools/`; registry pode ter vitrinezap.analisar_produto etc.
- **Serviços FastAPI:** mcp_service (7010), openmind (8001), ifood_service (7020), ddf_service, sparkscore_service, shopperbot_service, etc.
- **Feature flags:** `core.services.feature_flags` com `is_enabled(flag_name, ...)`.
- **Celery/Redis:** `core/services/task_queue_service` (celery_app, tasks, idempotency com Redis).

---

**Última atualização:** 2025-03-04
