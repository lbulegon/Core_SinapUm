# PR5 — Hardening + testes

Idempotência declarativa, timeouts/retries padronizados e bateria de testes (unit + smoke/integração).

## 1. Idempotência e timeouts/retries

### ToolVersion.is_idempotent
- **Modelo:** `app_mcp_tool_registry.models.ToolVersion` — campo `is_idempotent` (BooleanField, default False).
- **Migration:** `0005_add_is_idempotent_to_tool_version.py`.
- Uso futuro: ExecutionEngine ou mcp_service podem usar Redis (ex.: `core.services.task_queue_service.idempotency`) para dedupe quando a tool for declarada idempotente. Hoje o campo existe para uso declarativo; a dedupe por Redis fica como extensão opcional.

### ACP: timeouts e retries
- **ExecutionEngine:** constantes `DEFAULT_TIMEOUT` (ENV `ACP_MCP_TIMEOUT`, default 120) e `DEFAULT_MAX_RETRIES = 3`.
- **Por step:** no payload com `steps`, cada step pode ter `timeout_seconds`; o A2A plan já envia via `to_acp_payload()`.
- **ExecutionEngine:** usa `step.get("timeout_seconds") or timeout_seconds` por step; para chamada única, usa `state.get("max_retries") or DEFAULT_MAX_RETRIES`.

## 2. Testes unitários

Execução (a partir da raiz do projeto, com `pytest` instalado):
```bash
cd Core_SinapUm && pytest tests/unit/ -v --tb=short
```

| Arquivo | O que cobre |
|---------|-------------|
| `tests/unit/test_a2a_planner.py` | PlannerAgent: retorno A2APlan, fallback noop quando não há padrão, match de padrões (analise produto, catálogo, mrfoo), campos do step. |
| `tests/unit/test_mcp_uri.py` | parse_sinap_uri, validate_sinap_uri, is_sinap_uri (URIs sinap:// com/sem id e query). |
| `tests/unit/test_adapters.py` | BaseAdapter (get/list default None), adapter concreto (get/list com dados). |
| `tests/unit/test_a2a_executor.py` | ExecutorAgent use_acp=False: mock de `requests.post`; sucesso (COMPLETED) e falha (FAILED). |

## 3. Smoke / integração

| Arquivo | O que cobre |
|---------|-------------|
| `tests/integration/test_acp_a2a_smoke.py` | **ACP:** POST `/acp/tasks/` com payload noop, GET `/acp/tasks/<id>/`. **A2A:** POST `/a2a/run` com input mínimo. **Resources:** GET `/core/resources/` e `/core/resources/list/` sem uri (esperado 400). |

Requer Core Django rodando (ex.: `docker compose up web`). Falta de conexão ou rota não registrada gera skip.

```bash
pytest tests/integration/test_acp_a2a_smoke.py -v --tb=short
```

## 4. Compatibilidade

- Nenhum contrato de API alterado.
- Novo campo `is_idempotent` é opcional (default False).
- Timeouts/retries já existiam; apenas padronizados com constantes e suporte a timeout por step.
