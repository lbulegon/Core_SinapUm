# A2A — Agent to Agent (Core_SinapUm)

Orquestração mínima: **PlannerAgent** gera plano (steps) a partir do input; **ExecutorAgent** executa via ACP (AgentTask) ou direto via `/mcp/call`.

## Endpoints

- **POST /a2a/run** — Recebe `{ "input": "...", "context": {}, "idempotency_key": "opcional" }`. Retorna `{ "trace_id", "task_id", "status", "result" }`.
- **GET /a2a/tasks/<task_id>** — Proxy para estado da tarefa ACP (equivalente a GET /acp/tasks/<task_id>/).

## Fluxo

1. Validar A2A_ENABLED (default ON).
2. PlannerAgent gera plano (rule-based; padrões conhecidos → 1 step; senão step noop).
3. Se ACP_ENABLED: criar AgentTask e disparar run_acp_task; retornar task_id + trace_id.
4. Se ACP desligado: executar steps síncrono via /mcp/call e retornar result.

## Fallback do Planner

Se nenhum padrão conhecido for detectado, o planner gera um step com `tool_name="noop"`. É necessário existir uma tool `noop` (runtime noop) no registry MCP, ou o ACP falhará ao resolver. Alternativa: registrar em `app_mcp_tool_registry` uma Tool com nome `noop` e runtime `noop`.

## Compatibilidade

- Não altera `/acp/tasks/` nem `/mcp/call`. Apenas novas rotas namespaced `/a2a/*`.
