# CORE_SERVICE_PATTERN — Relatório de Scan do Core_SinapUm

**Data:** 2025-03-08  
**Objetivo:** Identificar padrões em /Core_SinapUm/services/ para guiar o architecture_intelligence_service.

---

## 1. Visão Geral dos Serviços

| Serviço | Stack | Porta | Descrição |
|---------|-------|-------|------------|
| shopperbot_service | FastAPI | 7030 | IA vendedora VitrineZap |
| openmind_service | FastAPI | 8001 | Análise imagens, agentes IA |
| creative_engine_service | FastAPI | - | Motor de criativos |
| sparkscore_service | FastAPI | 8006 | Análise psicológica/semiótica |
| ddf_service | FastAPI | 8005 | Detect & Delegate Framework |
| architecture_intelligence_service | FastAPI | 7025 | Meta-orbital arquitetural |

---

## 2. Padrão Estrutural

### 2.1 Estrutura Base (FastAPI)

service_name/
├── app/
│   ├── main.py
│   ├── api/ | routers/
│   ├── core/
│   ├── models/
│   └── ...
├── Dockerfile
├── requirements.txt
└── docker-compose.service.yml

### 2.2 Variações

- shopperbot: routers/, services/, schemas/, storage/, events/, utils/
- openmind: api/v1/endpoints/, core/, models/
- creative_engine: strategies/, creation/, learning/, adapters/
- ddf: providers/, mcp_tools/, core/, config/*.yaml

---

## 3. Padrões de Tasks

- DDF: TaskDelegate com YAML (providers, routes, policies)
- Creative Engine: job_processor
- ShopperBot: services como tasks síncronas
- Recomendação: tasks em app/tasks/, execução síncrona via API

---

## 4. Adapters Existentes

- DDF BaseProvider: execute(), is_available(), validate_input()
- Creative Engine: adapt(variant, context) -> Dict
- ShopperBot mcp_client: call_mcp_tool(tool_name, shopper_id, args)
- Recomendação: LLMAdapter, GraphAdapter, MCPAdapter

---

## 5. Padrões de Configuração

- Pydantic Settings (shopperbot, openmind): env_file=.env
- DDF: YAML (providers.yaml, routes.yaml, policies.yaml)
- Docker: environment, env_file

---

## 6. Padrões de Storage

- ShopperBot: CatalogStorage (PostgreSQL + psycopg2 pool)
- ShopperBot events: JSONL append em events.log
- DDF: Redis + PostgreSQL
- Recomendação: repositories por entidade, factory get_repository(backend)

---

## 7. Padrões de Eventos

- ShopperBot: EventEmitter, EventType enum, emit() -> log + JSONL
- Architecture Intelligence: EventBus, subscribe/emit
- Recomendação: manter EventBus com ArchitectureEvent

---

## 8. Integração Docker

- Build: context ./services/name, dockerfile Dockerfile
- Rede: mcp_network
- Portas: 7025 (architecture_intelligence), 8001 (openmind), etc.

---

## 9. Resumo para architecture_intelligence_service

| Aspecto | Padrão |
|---------|--------|
| Estrutura | app/core, pipelines, storage, adapters, tasks, events |
| Config | AIS_* env, pydantic/dataclass |
| Adapters | LLMAdapter, GraphAdapter, MCPAdapter |
| Storage | Repositories, get_repository(backend) |
| Eventos | EventBus, ArchitectureEvent |
