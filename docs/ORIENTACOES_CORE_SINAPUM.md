# Orientações — Core_SinapUm

Este documento reúne orientações para quem desenvolve ou opera o **Core_SinapUm**: setup, arquitetura, seeds, variáveis de ambiente e referências à documentação.

---

## Índice

1. [Visão geral do projeto](#1-visão-geral-do-projeto)
2. [Primeiros passos (setup)](#2-primeiros-passos-setup)
3. [WorldGraph (Neo4j) e seeds](#3-worldgraph-neo4j-e-seeds)
4. [Tools MCP e Resources sinap://](#4-tools-mcp-e-resources-sinap)
5. [Variáveis de ambiente](#5-variáveis-de-ambiente)
6. [Testes](#6-testes)
7. [Documentação de referência](#7-documentação-de-referência)
8. [Regras importantes (não quebrar)](#8-regras-importantes-não-quebrar)

---

## 1. Visão geral do projeto

O **Core_SinapUm** é o núcleo de orquestração que expõe:

- **MCP** (Model Context Protocol): tools versionadas, resources `sinap://`, prompts, telemetria.
- **ACP** (Agent Communication Protocol): tarefas, retry, timeout, estado em PostgreSQL/Redis.
- **A2A** (Agent to Agent): Planner + Executor, fluxo colaborativo.
- **WorldGraph** (Neo4j): memória diagramática; subgrafo MrFoo (FKG) com labels `MRFOO_*`.
- **Adapters**: camada que encapsula chamadas a serviços externos (VitrineZap, MotoPro, MrFoo).

Novas funcionalidades devem ser **aditivas**: novos arquivos, novos includes, feature flags. Não alterar rotas ou comportamentos já em produção sem estratégia de migração.

---

## 2. Primeiros passos (setup)

```bash
cd /root/Core_SinapUm
cp .env.example .env   # ajustar variáveis conforme o ambiente
docker compose up -d db
docker compose up -d web
```

Para desenvolvimento com MCP Service e WorldGraph:

```bash
docker compose up -d worldgraph_service
docker compose up -d mcp_service   # se existir no compose
```

Migrações:

```bash
docker compose run --rm web python manage.py migrate
```

---

## 3. WorldGraph (Neo4j) e seeds

### Subir o Neo4j

```bash
cd /root/Core_SinapUm
docker compose up -d worldgraph_service
```

Servidor Core: **69.169.102.84**. Portas: **7474** (HTTP/Browser), **7687** (BOLT). Para o MrFoo em outro host (ex.: Railway), configurar `WORLDGRAPH_BOLT_URL=bolt://69.169.102.84:7687` e liberar a porta 7687 no firewall. Senha padrão no compose: `neo4j12345` (ou valor de `WORLDGRAPH_NEO4J_PASSWORD` no `.env`).

### Seed do schema MrFoo (FKG)

Idempotente (MERGE). Cria constraints/indexes e nós de TimeSlots (ALMOCO, JANTAR, MADRUGADA):

```bash
docker compose exec -T worldgraph_service cypher-shell -u neo4j -p neo4j12345 < services/worldgraph_service/seed/mrfoo_schema_v1.cypher
```

Substituir `neo4j12345` pela senha configurada no ambiente, se diferente.

### Outros seeds no WorldGraph

- `services/worldgraph_service/seed/001_schema.cypher` — schema base (Agent, Object, Place, Event). Não remover nem alterar; apenas adicionar novos seeds em arquivos separados.

---

## 4. Tools MCP e Resources sinap://

### Seed das tools no Registry (Django)

- **Registry geral** (vitrinezap, sparkscore, etc.): executado no entrypoint do container `web` ou manualmente via comando de seed do app.
- **Tools MrFoo (FKG)**:

```bash
docker compose run --rm web python manage.py seed_mrfoo_graph_tools
```

Isso cria as tools: `mrfoo.graph.status`, `mrfoo.graph.sync_full`, `mrfoo.graph.sync_incremental`, `mrfoo.graph.margin_per_minute`, `mrfoo.graph.complexity_score`, `mrfoo.graph.combo_suggestions`, `mrfoo.graph.new_item_suggestions`.

### Resources sinap://

Handlers registrados em `adapters/register_resources.py`. Exemplos:

- `sinap://mrfoo/graph/status?tenant_id=1`
- `sinap://mrfoo/graph/insights/margin_per_minute?tenant_id=1&timeslot=JANTAR`
- `sinap://vitrinezap/catalog/<id>?shopper_id=...`

O Core **não calcula** regra de negócio dos verticais; delega ao adapter (HTTP ao serviço correspondente). Tenant: header **X-Tenant-ID** (padrão documentado).

### Execução de tools

- **Direto no Core:** `POST /core/tools/<tool_name>/execute/` com body `{"input": {...}}`.
- **Via MCP Service:** `POST /mcp/call` com `{"tool": "mrfoo.graph.status", "input": {"tenant_id": "1"}}`. Para runtime `mrfoo_graph`, o MCP Service delega para o Core.

---

## 5. Variáveis de ambiente

Principais variáveis (ver `.env.example` e `docs/ENV_CORE_SINAPUM_EXEMPLO.md`):

| Variável | Uso |
|----------|-----|
| `DATABASE_URL` | PostgreSQL do Core |
| `WORLDGRAPH_NEO4J_USER` / `WORLDGRAPH_NEO4J_PASSWORD` | Neo4j (WorldGraph) |
| `MRFOO_BASE_URL` | Base da API MrFoo. Desenvolvimento: `https://mrfoo-development.up.railway.app` (Railway). |
| `MRFOO_API_TOKEN` | Token Bearer para API MrFoo (opcional) |
| `SINAPUM_CORE_URL` | URL do Core (usado pelo MCP Service para resolve/execute) |
| Feature flags | `docs/ENV_FEATURE_FLAGS.md` (ex.: `ACP_ENABLED`, `MCP_RESOURCES_ENABLED`, `A2A_ENABLED`, `DUAL_RUN_ENABLED`) |

---

## 6. Testes

- **Unitários:** `pytest tests/unit/ -v`
- **Integração/smoke:** `pytest tests/integration/ -v`
- **Adapters (incl. MrFoo):** `pytest tests/unit/test_adapters.py -v`

Detalhes em `tests/README.md`.

---

## 7. Documentação de referência

| Documento | Conteúdo |
|-----------|----------|
| [AVALIACAO_CORE_SINAPUM_PARA_CHATGPT.md](AVALIACAO_CORE_SINAPUM_PARA_CHATGPT.md) | Visão geral do Core para uso com IAs (ex.: ChatGPT) |
| [MRFOO_FOOD_GRAPH_INTEGRATION.md](MRFOO_FOOD_GRAPH_INTEGRATION.md) | Integração FKG: WorldGraph, adapter, tools, resources |
| [STATUS_ARQUITETURA_MCP_ACP_A2A.md](STATUS_ARQUITETURA_MCP_ACP_A2A.md) | Status da arquitetura MCP/ACP/A2A |
| [PLANO_PROXIMA_LEVA_PRS.md](PLANO_PROXIMA_LEVA_PRS.md) | Plano de PRs (A2A, adapters, feature flags, observabilidade, testes) |
| [PR3_FEATURE_FLAGS_DUAL_RUN.md](PR3_FEATURE_FLAGS_DUAL_RUN.md) | Feature flags e dual-run |
| [PR4_OBSERVABILIDADE.md](PR4_OBSERVABILIDADE.md) | Tokens, custo, latência no MCP Service |
| [PR5_HARDENING_TESTES.md](PR5_HARDENING_TESTES.md) | Idempotência, timeouts, testes |
| [MEMORIA_DIAGRAMATICA_E_SEMANTICA.md](MEMORIA_DIAGRAMATICA_E_SEMANTICA.md) | WorldGraph (Neo4j) e memória semântica |
| [ENV_CORE_SINAPUM_EXEMPLO.md](ENV_CORE_SINAPUM_EXEMPLO.md) | Exemplo de variáveis de ambiente |

---

## 8. Regras importantes (não quebrar)

- **Não remover** seeds existentes do WorldGraph; apenas **adicionar** novos seeds (ex.: `mrfoo_schema_v1.cypher`) idempotentes.
- **Não duplicar** regra de negócio no Core: o Core orquestra; cálculos de domínio ficam nos serviços (ex.: MrFoo).
- **Não alterar** rotas existentes; apenas **adicionar** novas rotas e `include()`.
- **Sempre filtrar** por `tenant_id` e `vertical="mrfoo"` em dados do subgrafo MrFoo.
- **Compatibilidade**: manter feature flags, dual-run e testes existentes; mudanças devem ser aditivas e, quando possível, ativáveis por flag.

---

**Última atualização:** março 2026  
**Escopo:** Core_SinapUm (MCP, ACP, A2A, WorldGraph, MrFoo FKG)
