# app_acp — Agent Communication Protocol

App Django para **gerenciamento de tarefas de agente** (ACP): criação, execução assíncrona via Celery, consulta de status e cancelamento.

## Modelo

- **AgentTask**: task_id (UUID), agent_name, status (PENDING/RUNNING/WAITING/FAILED/COMPLETED/CANCELLED), payload, result, error, trace_id, retry_count, max_retries, timeout_seconds, idempotency_key, timestamps.

## API (rotas aditivas)

- **POST /acp/tasks/** — Cria tarefa e enfileira execução.
  - Body: `{ "agent_name": "...", "payload": { "tool": "...", "version": "...", "input": {...} } ou { "steps": [...] }, "trace_id?", "max_retries?", "timeout_seconds?", "idempotency_key?" }`
- **GET /acp/tasks/<task_id>/** — Retorna estado da tarefa.
- **POST /acp/tasks/<task_id>/cancel/** — Cancela se PENDING ou WAITING.

## Fluxo

1. Cliente chama POST /acp/tasks/ com agent_name e payload.
2. TaskManager cria AgentTask (PENDING) e chama `run_acp_task.delay(task_id)` (Celery).
3. Worker executa ExecutionEngine.run_task(task_id): chama MCP (POST /mcp/call) conforme payload (tool única ou steps), atualiza status/result/error no Postgres.
4. Cliente consulta GET /acp/tasks/<task_id>/ para obter status e result.

## Integração

- **Celery**: task `app_acp.tasks.run_acp_task`; autodiscover em `core.services.task_queue_service.celery_app`.
- **MCP**: ExecutionEngine chama MCP Service (MCP_SERVICE_URL ou MCP_CALL_URL) para executar tools.
- Nenhum endpoint ou fluxo legado é alterado.
