# Avaliação do Core_SinapUm — O que já temos (para ChatGPT)

**Objetivo:** Documento de referência para apresentar ao ChatGPT o estado atual do monorepo **Core_SinapUm**, permitindo que a IA proponha evoluções, integrações ou novos módulos de forma alinhada ao que já existe.

**Última atualização:** 2025-03-04

---

## 1. Visão geral do Core_SinapUm

O **Core_SinapUm** é um **monorepo** que atua como:

- **Núcleo cognitivo** de orquestração (MCP + ACP + A2A).
- **Registry central** de tools, prompts e resources para agentes e LLMs.
- **Gateway** para serviços de IA (OpenMind), WhatsApp (Evolution/Baileys), iFood, DDF, SparkScore, memória (Neo4j + FAISS), etc.

**Stack principal:** Django 6, PostgreSQL, Redis, Celery, Docker. Serviços auxiliares em FastAPI (MCP Service, Vectorstore, DDF, SparkScore, etc.).

---

## 2. Arquitetura MCP + ACP + A2A (implementada)

### 2.1 MCP (Model Context Protocol)

| Componente | O que temos |
|------------|-------------|
| **Tool Registry** | App `app_mcp_tool_registry`: modelos `Tool`, `ToolVersion`, `ClientApp`, `ToolCallLog`. Resolução de tools por nome/versão; input/output schema. |
| **Gateway de execução** | Serviço FastAPI `services/mcp_service`: `POST /mcp/call` recebe `{ tool, version?, input, context_pack? }`, resolve tool no Core, executa runtime (noop, prompt, openmind_http, pipeline, ddf). |
| **Context Pack** | `request_id`, `trace_id`, actor, source; normalização e repasse para tools. |
| **Telemetria** | `ToolCallLog` com `tokens_in`, `tokens_out`, `cost_usd`, `model`, `provider` (nullable). `mcp_service` extrai usage do runtime (OpenAI-style) e envia no `POST /core/tools/log/`. |
| **Prompts versionados** | Convenção `vertical/purpose/vN` em `app_mcp_tool_registry.utils`; suporte a refs antigas. |
| **MCP Resources** | Parser de URIs `sinap://vertical/entity/id` em `mcp/uri.py`; resolver e registry de handlers em `mcp/resources/`; endpoints `GET /core/resources/?uri=...` e `GET /core/resources/list/?uri=...`. Handlers registrados via `adapters/register_resources.py` (vitrinezap, motopro, mrfoo, etc.). |

### 2.2 ACP (Agent Communication Protocol)

| Componente | O que temos |
|------------|-------------|
| **Modelo de tarefa** | App `app_acp`: modelo `AgentTask` (task_id, agent_name, status, payload, result, error, trace_id, retry_count, max_retries, timeout_seconds, idempotency_key). |
| **TaskManager** | Cria tarefa, consulta estado, cancelamento; idempotência por `idempotency_key` (reutiliza tarefa existente). |
| **ExecutionEngine** | Executa payload (tool única ou steps); chama MCP via `POST /mcp/call`; timeout e retries padronizados; suporte a timeout por step. |
| **StateStore** | Persistência em PostgreSQL (AgentTask). |
| **Celery** | Task `run_acp_task` enfileirada pelo TaskManager; integração com `core.services.task_queue_service`. |
| **API REST** | `POST /acp/tasks/` (criar), `GET /acp/tasks/<task_id>/` (consultar), `POST /acp/tasks/<task_id>/cancel/` (cancelar). |

### 2.3 A2A (Agent to Agent)

| Componente | O que temos |
|------------|-------------|
| **PlannerAgent** | `a2a/planner_agent.py`: entrada `user_input` + context; saída `A2APlan` (intent, steps). Fallback rule-based (padrões → tool conhecida; senão step `noop`). |
| **ExecutorAgent** | `a2a/executor_agent.py`: executa plano via ACP (AgentTask) ou de forma síncrona chamando `/mcp/call` por step. |
| **Schemas** | `a2a/schemas.py`: `PlanStep`, `A2APlan`; `to_acp_payload()` com steps e `timeout_seconds`. |
| **Endpoints** | `POST /a2a/run` (body: input, context?, idempotency_key?); `GET /a2a/tasks/<task_id>/` (proxy para ACP). |

### 2.4 Feature flags e dual-run

- **Flags (ENV / core.services.feature_flags):** `ACP_ENABLED`, `MCP_RESOURCES_ENABLED`, `A2A_ENABLED`, `DUAL_RUN_ENABLED`.
- **Comportamento:** A2A desligado → 503; ACP desligado → `/a2a/run` executa síncrono via MCP; MCP Resources desligado → `/core/resources/` retorna 404 controlado; dual-run → executa caminho sync + principal e loga com `trace_id`.

### 2.5 Adapters

- **Pasta `adapters/`:** `BaseAdapter`, `vitrinezap_adapter` (implementado, usa `app_mcp.clients.VitrineZapClient`); stubs: `motopro_adapter`, `mrfoo_adapter`, `openmind_adapter`, `ifood_adapter`, `ddf_adapter`.
- **Uso:** Tools em `app_mcp/tools/` (catalog, order, cart, customer) chamam adapters; handlers de resources `sinap://` registrados em `adapters/register_resources.py`, chamados no `ready()` do `app_mcp_tool_registry`.

### 2.6 Hardening e testes

- **ToolVersion.is_idempotent** (campo booleano; Redis dedupe opcional).
- **Constantes ACP:** `DEFAULT_TIMEOUT`, `DEFAULT_MAX_RETRIES`; timeout por step no plano.
- **Testes unit:** `tests/unit/` — PlannerAgent, ExecutorAgent (sync + mock), parser URI sinap://, adapters.
- **Smoke/integração:** `tests/integration/test_acp_a2a_smoke.py` — ACP, A2A, Resources.

---

## 3. Aplicações Django (principais)

| App | Função |
|-----|--------|
| **app_sinapum** | Home, análise de imagem, API analyze-product-image, integração Évora. |
| **app_mcp_tool_registry** | Registry MCP: tools, versions, client_apps, ToolCallLog; URLs `/core/tools/`, `/core/resources/`, `/core/tools/log/`, resolve prompt. |
| **app_mcp** | Tools MCP (catalog, order, cart, customer, etc.) e clients (VitrineZap); integração com adapters. |
| **app_acp** | AgentTask, TaskManager, ExecutionEngine, StateStore, Celery task, API `/acp/tasks/`. |
| **app_whatsapp** / **app_whatsapp_gateway** | WhatsApp plugável e gateway (Evolution/Baileys). |
| **app_whatsapp_events** | Eventos canônicos WhatsApp. |
| **app_ifood_integration** | Integração iFood. |
| **app_leads** | Lead Registry. |
| **app_creative_engine** | Motor de criativos. |
| **app_conversations** | Conversas e sugestões de IA. |
| **app_ai_bridge** | Ponte com OpenMind. |
| **app_inbound_events** | Eventos brutos (auditoria + dedupe). |

---

## 4. Serviços (Docker Compose)

| Serviço | Container / imagem | Função |
|---------|--------------------|--------|
| **db** | postgres:16-alpine | PostgreSQL principal. |
| **web** | Django (Gunicorn) | Core Registry, admin, APIs, health. |
| **openmind** | openmind_service | IA (LLM). |
| **mcp_service** | FastAPI | Gateway MCP: `/mcp/call`, list tools; chama Core para resolver e executa runtimes. |
| **ddf_service** | DDF | Detect & Delegate Framework. |
| **ifood_service** | iFood | Integração iFood. |
| **sparkscore_service** | SparkScore | Análise psicológica/semiótica. |
| **worldgraph_service** | neo4j:5 | Memória diagramática (Neo4j); portas 7474 (HTTP), 7687 (BOLT). |
| **vectorstore_service** | FastAPI + FAISS | Memória semântica; porta 8010. |
| **whatsapp_gateway_service** | Node/Baileys | Gateway WhatsApp. |
| **shopperbot_service** | ShopperBot | Recomendações. |
| **mlflow** | MLflow | Experimentos ML. |
| **chatwoot_*** | Chatwoot | Atendimento (Rails, Sidekiq, Redis, Postgres). |

---

## 5. Endpoints principais (Core Django)

- **Health:** `/health`, `/healthz`, etc.
- **Core MCP:** `/core/tools/`, `/core/tools/resolve/`, `POST /core/tools/log/`, `GET /core/resources/?uri=`, `GET /core/resources/list/?uri=`.
- **ACP:** `POST /acp/tasks/`, `GET /acp/tasks/<id>/`, `POST /acp/tasks/<id>/cancel/`.
- **A2A:** `POST /a2a/run`, `GET /a2a/tasks/<task_id>/`.
- **Análise:** `/analyze/`, `api/v1/analyze-product-image`.
- **WhatsApp:** `/whatsapp/`, `/webhooks/whatsapp/`, `api/whatsapp/`, `api/v1/whatsapp/events/`.
- **iFood, leads, creative-engine, admin:** conforme includes em `setup/urls.py`.

---

## 6. Memória (Neo4j + FAISS)

- **WorldGraph (Neo4j):** Serviço `worldgraph_service`; variáveis `WORLDGRAPH_NEO4J_USER`, `WORLDGRAPH_NEO4J_PASSWORD`, `WORLDGRAPH_HTTP_PORT`, `WORLDGRAPH_BOLT_PORT`; volumes `worldgraph_data`, `worldgraph_logs`; seed em `services/worldgraph_service/seed/`. Documentação: `docs/MEMORIA_DIAGRAMATICA_E_SEMANTICA.md`, `services/worldgraph_service/README.md`.
- **Vectorstore (FAISS):** Serviço `vectorstore_service`; memória semântica; ponte com Neo4j (ids retornados por busca podem ser usados em Cypher).

---

## 7. Verticais e tools MCP (referência)

- **vitrinezap:** catalog, order, cart, customer; adapter implementado; resources `sinap://vitrinezap/catalog`, etc.
- **motopro:** slots.allocate, routes.optimize; adapter stub; resources stub.
- **mrfoo:** menu.generate, shopping_list.generate; adapter stub; resources stub (para integrar com o projeto MrFoo).
- **openmind, ifood, ddf:** adapters stubs; uso conforme evolução dos serviços.

---

## 8. Documentação de suporte

- **Status arquitetura:** `docs/STATUS_ARQUITETURA_MCP_ACP_A2A.md`
- **Plano PRs:** `docs/PLANO_PROXIMA_LEVA_PRS.md`
- **PRs concluídos:** `docs/PR3_FEATURE_FLAGS_DUAL_RUN.md`, `docs/PR4_OBSERVABILIDADE.md`, `docs/PR5_HARDENING_TESTES.md`
- **Memória:** `docs/MEMORIA_DIAGRAMATICA_E_SEMANTICA.md`
- **Serviços:** `docs/ARQUITETURA_SERVICOS.md`
- **Adapters:** `adapters/README.md`; **A2A:** `a2a/README.md`; **ACP:** `app_acp/README.md`; **MCP:** `mcp/README.md`

---

## 9. Como usar este documento com o ChatGPT

- **Copie ou anexe** este arquivo (ou trechos) ao prompt.
- **Contexto sugerido:** “O Core_SinapUm já tem MCP, ACP, A2A, adapters, feature flags, observabilidade e testes (PR1–PR5). Neo4j (WorldGraph) e FAISS (Vectorstore) estão no docker-compose. Preciso que [descreva a tarefa] sem quebrar o legado e respeitando a arquitetura existente.”
- **Para integrar um novo vertical (ex.: MrFoo):** use a seção 7 e o padrão de adapter + resources + tools; referência ao levantamento do MrFoo em `Source/mrfoo/docs/LEVANTAMENTO_E_DESCRICAO_PROJETO_MRFOO.md`.

---

## 10. Resumo em uma frase

**Core_SinapUm** é um monorepo Django com arquitetura MCP + ACP + A2A já implementada (registry de tools, gateway MCP, resources sinap://, AgentTask, Planner/Executor, adapters, feature flags, observabilidade, testes), serviços em Docker (PostgreSQL, Redis, Celery, OpenMind, MCP Service, Neo4j, FAISS, WhatsApp, DDF, SparkScore, iFood, etc.), e documentação de status e plano para evoluções sem quebrar legado.
