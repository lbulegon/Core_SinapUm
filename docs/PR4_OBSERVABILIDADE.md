# PR4 — Observabilidade (tokens/custo no mcp_service)

Telemetria de uso de LLM persistida no ToolCallLog; falha de captura não quebra a execução.

## O que foi feito

### 1. Extração de usage no MCP Service (`services/mcp_service/main.py`)

- **`extract_usage_from_runtime_output(output_data)`**: extrai do retorno do runtime:
  - **usage**: formato tipo OpenAI (`prompt_tokens`, `completion_tokens`, `input_tokens`, `output_tokens`, `total_tokens`)
  - **model** / **provider**: no top-level ou em `output_data["data"]` (respostas aninhadas)
  - **cost_usd**: se vier na resposta; senão, estimativa best-effort para `gpt-4o`/`gpt-4` e `gpt-3.5` (valores por 1M tokens aproximados)
- Uso dentro de `try/except`: falha na extração só gera log em debug e retorna dict vazio.

### 2. Payload do log

- **`log_tool_call(..., tokens_in=, tokens_out=, cost_usd=, model=, provider=)`**: parâmetros opcionais adicionados.
- O payload enviado a `POST /core/tools/log/` passa a incluir, quando disponíveis:
  - `tokens_in`, `tokens_out`, `cost_usd`, `model`, `provider`
- O Core (`app_mcp_tool_registry/views.log_tool_call`) já aceitava esses campos; nenhuma alteração no Django foi necessária.

### 3. Fluxo no `/mcp/call`

- Após `execute_runtime()` retornar com sucesso:
  1. Chama-se `extract_usage_from_runtime_output(output_data)` (com try/except).
  2. O resultado é repassado para `log_tool_call(..., tokens_in=..., tokens_out=..., cost_usd=..., model=..., provider=...)`.
- Em caminhos de erro (HTTPError, ValueError, Exception), o log segue sendo registrado sem telemetria de usage (campos permanecem null).

## Compatibilidade

- Campos no `ToolCallLog` continuam nullable; ausência de usage apenas deixa esses campos em branco.
- Nenhum contrato de API foi alterado; apenas o preenchimento dos campos já existentes no log.
