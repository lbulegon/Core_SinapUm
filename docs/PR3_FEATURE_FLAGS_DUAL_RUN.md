# PR3 — Feature flags + dual-run

Flags por capacidade; dual-run opcional com logging; fallback sempre disponível.

## Flags (ENV ou DB)

| Flag | Default | Uso |
|------|---------|-----|
| **ACP_ENABLED** | true | Se false, `/a2a/run` executa steps síncrono via `/mcp/call` (sem criar AgentTask). |
| **MCP_RESOURCES_ENABLED** | true | Se false, `GET /core/resources/` e `/core/resources/list/` retornam 404 com `code: MCP_RESOURCES_DISABLED`. |
| **A2A_ENABLED** | true | Se false, `POST /a2a/run` retorna 503 com `code: A2A_DISABLED`. |
| **DUAL_RUN_ENABLED** | false | Se true, em `/a2a/run` executa também o caminho sync (além do principal) e loga resultado com `trace_id` para comparação. |

Leitura: `core.services.feature_flags` (is_enabled); definição em `core/services/feature_flags/settings.py` (FEATURE_FLAGS) e ENV.

## Comportamento

- **Defaults** mantêm comportamento atual (tudo ON exceto DUAL_RUN).
- **MCP_RESOURCES_ENABLED=false**: resources retornam 404 com mensagem controlada; não quebra quem não chama resources.
- **ACP_ENABLED=false**: resposta de `/a2a/run` vem síncrona (result no body); não quebra quem já usa task_id assíncrono (eles podem checar status).
- **DUAL_RUN_ENABLED=true**: best effort — executa sync, loga; depois executa caminho principal; retorno é o do caminho principal. Logs permitem comparação posterior por `trace_id`.

## Compatibilidade

- Nenhum contrato de resposta foi alterado; apenas comportamentos condicionados às flags.
- Desligar flags só restringe quando explicitamente false.
