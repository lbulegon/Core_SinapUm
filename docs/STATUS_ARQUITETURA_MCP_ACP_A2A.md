# Status da Arquitetura MCP + ACP + A2A — Core_SinapUm

**Última atualização:** 2025-03-04

---

## O que já está sólido (implementado)

| Camada | O que temos | Observação |
|--------|-------------|------------|
| **MCP (parcial)** | Registry de tools, gateway `/mcp/call`, Context Pack, trace_id, ToolCallLog | Já existia; reforçado com telemetria (tokens/custo nullable) |
| **MCP Resources** | Parser `sinap://`, resolver, registry de handlers, endpoints `/core/resources/` e `/core/resources/list/` | Estrutura pronta; handlers são registrados quando adapters existirem |
| **Prompts versionados** | Convenção `vertical/purpose/vN` no resolver; refs antigas mantidas | `app_mcp_tool_registry.utils` |
| **ACP** | Modelo `AgentTask`, TaskManager, ExecutionEngine, StateStore, task Celery `run_acp_task`, API `/acp/tasks/` (criar, consultar, cancelar) | App `app_acp` completo; execução via MCP |
| **Infra** | PostgreSQL, Redis, Celery, Docker, variáveis MCP/ACP no `.env` | Integração com `task_queue_service` |
| **Legado** | Nenhum endpoint antigo alterado; novas rotas namespaced (`/acp/`, `/core/resources/`, `/a2a/`) | Retrocompatibilidade mantida |
| **A2A** | `a2a/` com PlannerAgent e ExecutorAgent; `POST /a2a/run`, `GET /a2a/tasks/<id>`; fallback sync quando ACP desligado | PR1 |
| **Adapters** | `adapters/` com BaseAdapter, vitrinezap (implementado), stubs motopro/mrfoo/openmind/ifood/ddf; tools e resources usando adapters | PR2 |
| **Feature flags** | ACP_ENABLED, MCP_RESOURCES_ENABLED, A2A_ENABLED, DUAL_RUN_ENABLED; uso em `/a2a/run` e `/core/resources/`; dual-run com log por trace_id | PR3 |
| **Observabilidade** | `mcp_service`: extração de usage do runtime, envio de tokens/custo/model no log; estimativa de custo para gpt-4o/gpt-3.5 | PR4 |
| **Hardening** | ToolVersion.is_idempotent; timeouts/retries padronizados no ACP; testes unit (Planner, Executor, URI, adapters) e smoke ACP/A2A/Resources | PR5 |

---

## O que ainda falta (em relação ao plano)

Nenhum item pendente da leva PR1–PR5.

---

## Conclusão

- **Base sólida:** MCP, ACP, A2A, adapters, feature flags, observabilidade e hardening/testes (PR1–PR5) implementados; retrocompatibilidade mantida.

