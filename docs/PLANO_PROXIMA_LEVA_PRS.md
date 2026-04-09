# Plano da Próxima Leva de PRs — Core_SinapUm (MCP + ACP + A2A)

**Objetivo:** Implementar A2A explícito, Adapters, Feature flags + dual-run, Observabilidade e Hardening **sem quebrar legado**.

---

## 1) Plano de Execução (PR1..PR5)

### PR1 — A2A minimal (Planner/Executor + endpoint)
- Criar pasta `a2a/` com `schemas.py` (plano: intent, steps[], expected_output).
- Implementar `PlannerAgent`: entrada user_input + context; saída plano; fallback rule-based sem LLM (padrões conhecidos → 1–3 steps; senão step noop/prompt).
- Implementar `ExecutorAgent`: entrada plano + context; criar AgentTask ACP ou chamar `/mcp/call` step-by-step; saída results + trace_id + status; idempotência com idempotency_key.
- Endpoint `POST /a2a/run`: validar A2A_ENABLED (default ON), Planner → criar AgentTask → retornar task_id + trace_id.
- Endpoint `GET /a2a/tasks/<task_id>`: proxy para `GET /acp/tasks/<task_id>/`.
- Registrar rotas em Django (`/a2a/run`, `/a2a/tasks/<uuid:task_id>/`).

### PR2 — Adapter layer — ✅
- Criar pasta `adapters/` com `base.py` (interface) e módulos: `vitrinezap_adapter`, `motopro_adapter`, `mrfoo_adapter`, `openmind_adapter`, `ifood_adapter`, `ddf_adapter`.
- Cada adapter expõe funções estáveis (ex.: get_catalog, send_message, allocate_slot); chama clients/endpoints/serviços existentes.
- Refatorar tools em `app_mcp/tools/` para chamar adapters (sem duplicar lógica).
- Registrar handlers MCP Resources via adapters: sinap://vitrinezap/catalog/{id}, sinap://motopro/orders/{id}, sinap://mrfoo/menu/{id}.

### PR3 — Feature flags + dual-run — ✅
- Flags: ACP_ENABLED, MCP_RESOURCES_ENABLED, A2A_ENABLED, DUAL_RUN_ENABLED (leitura via core.services.feature_flags + ENV).
- Em `/a2a/run`: se ACP_ENABLED false → executar steps direto via `/mcp/call` (síncrono).
- Em `/core/resources/`: se MCP_RESOURCES_ENABLED false → 404 com mensagem controlada.
- Dual-run: quando DUAL_RUN_ENABLED true, executa caminho sync e loga com trace_id; depois executa caminho principal.
- Defaults: todos ON exceto DUAL_RUN_ENABLED (false).

### PR4 — Observabilidade (tokens/custo no mcp_service) — ✅
- No `services/mcp_service`: `extract_usage_from_runtime_output()` extrai usage (OpenAI-style) do retorno do runtime; suporta respostas aninhadas em `data`; estimativa de custo para gpt-4o/gpt-3.5 quando usage disponível.
- Persistir tokens_in, tokens_out, cost_usd, model, provider no payload enviado a `POST /core/tools/log/`.
- try/except para que falha de captura não quebre execução.

### PR5 — Hardening + testes — ✅
- Idempotência declarativa: campo `ToolVersion.is_idempotent` (migration 0005); Redis para dedupe deixado como extensão opcional.
- Timeouts/retries: DEFAULT_TIMEOUT, DEFAULT_MAX_RETRIES no ExecutionEngine; timeout por step em `to_acp_payload()` e no engine.
- Testes unit: `tests/unit/` — PlannerAgent (fallback, padrões), ExecutorAgent (sync + mock), URI parser, adapters.
- Smoke/integração: `tests/integration/test_acp_a2a_smoke.py` — POST/GET `/acp/tasks/`, POST `/a2a/run`, GET `/core/resources/` e `/core/resources/list/`.

---

## 2) Estrutura de pastas NOVAS (somente o que será criado)

```
Core_SinapUm/
├── a2a/
│   ├── __init__.py
│   ├── schemas.py          # A2A plan schema
│   ├── planner_agent.py     # PlannerAgent
│   ├── executor_agent.py    # ExecutorAgent
│   └── README.md
│
├── adapters/
│   ├── __init__.py
│   ├── base.py             # Interface/base
│   ├── vitrinezap_adapter.py
│   ├── motopro_adapter.py
│   ├── mrfoo_adapter.py
│   ├── openmind_adapter.py
│   ├── ifood_adapter.py
│   └── ddf_adapter.py
│
└── (modificações em arquivos existentes: setup/urls.py, app_mcp/tools/*, mcp/resources/resolver.py, services/mcp_service/main.py, core/services/feature_flags, etc.)
```

---

## 3) Schemas

### A2A Plan (JSON)
```json
{
  "intent": "string",
  "steps": [
    {
      "id": "step_1",
      "tool_name": "vitrinezap.analisar_produto",
      "tool_version": "1.0",
      "args": {},
      "resources": ["sinap://vitrinezap/catalog/123"],
      "depends_on": [],
      "timeout_seconds": 60
    }
  ],
  "expected_output": {}
}
```

### POST /a2a/run — Request
```json
{
  "input": "texto ou comando do usuário",
  "context": {},
  "idempotency_key": "opcional"
}
```

### POST /a2a/run — Response
```json
{
  "trace_id": "uuid",
  "task_id": "uuid",
  "status": "PENDING",
  "result": null
}
```

### AgentTask (resumo, já existente)
- task_id, agent_name, status, payload (com steps ou tool+input), result, error, trace_id, retry_count, max_retries, timeout_seconds, idempotency_key, created_at, updated_at, started_at, finished_at.

---

## 4) Lista de arquivos a criar/modificar

### PR1 (A2A minimal)
| Ação  | Path |
|-------|------|
| CREATE | `a2a/__init__.py` |
| CREATE | `a2a/schemas.py` |
| CREATE | `a2a/planner_agent.py` |
| CREATE | `a2a/executor_agent.py` |
| CREATE | `a2a/README.md` |
| CREATE | `a2a/views.py` (endpoints /a2a/run e proxy /a2a/tasks/<id>) |
| CREATE | `a2a/urls.py` |
| MODIFY | `setup/urls.py` (include a2a.urls) |

### PR2 (Adapters)
| Ação  | Path |
|-------|------|
| CREATE | `adapters/__init__.py`, `base.py`, `vitrinezap_adapter.py`, `motopro_adapter.py`, `mrfoo_adapter.py`, `openmind_adapter.py`, `ifood_adapter.py`, `ddf_adapter.py` |
| MODIFY | `app_mcp/tools/*.py` (chamar adapters) |
| MODIFY | `mcp/resources/resolver.py` ou módulo de bootstrap (register_resource_handler com adapters) |

### PR3 (Flags + dual-run)
| Ação  | Path |
|-------|------|
| MODIFY | `a2a/views.py` (checar A2A_ENABLED, ACP_ENABLED; dual-run se DUAL_RUN_ENABLED) |
| MODIFY | `app_mcp_tool_registry/views.py` (resource_get/resource_list: checar MCP_RESOURCES_ENABLED) |
| MODIFY | `.env` / docs (ACP_ENABLED, MCP_RESOURCES_ENABLED, A2A_ENABLED, DUAL_RUN_ENABLED) |
| MODIFY | `core/services/feature_flags` ou leitura ENV direta onde necessário |

### PR4 (Observabilidade)
| Ação  | Path |
|-------|------|
| MODIFY | `services/mcp_service/main.py` (capturar tokens/custo; enviar no log) |
| MODIFY | Payload para `/core/tools/log/` (tokens_in, tokens_out, cost_usd) — já suportado no Core |

### PR5 (Hardening + testes)
| Ação  | Path |
|-------|------|
| MODIFY | `app_mcp_tool_registry/models.py` (idempotency em ToolVersion opcional) |
| MODIFY | `services/mcp_service/main.py`, `app_acp/execution_engine.py` (aplicar idempotência, timeouts) |
| CREATE | `tests/test_a2a.py`, `tests/test_adapters.py`, `tests/test_acp_integration.py`, smoke tests |

---

## 5) Notas de compatibilidade (por que nada quebra)

- **PR1:** Apenas novas rotas `/a2a/run` e `/a2a/tasks/<id>`. Não altera `/acp/tasks/` nem `/mcp/call`. ACP continua chamável direto.
- **PR2:** Adapters são nova camada; tools existentes passam a delegar a adapters sem mudar assinatura pública (ou nova ToolVersion se necessário). Resources handlers são registrados de forma aditiva.
- **PR3:** Flags com default ON; desligar só restringe quando explicitamente false. Dual-run é opt-in (DUAL_RUN_ENABLED).
- **PR4:** Campos tokens/custo já são nullable no ToolCallLog; preenchimento é aditivo; falha de captura não quebra (try/except).
- **PR5:** Idempotência e timeouts são aditivos; testes não alteram comportamento de produção.

---

Agora executo o **PR1 (A2A minimal)** e gero o código.
