# MCP — Model Context Protocol (convenção Core_SinapUm)

Esta pasta é **estrutura de referência** para MCP no Core_SinapUm. As implementações reais continuam em:

- **Registry e API HTTP:** `app_mcp_tool_registry` (Django), endpoints `/core/tools/resolve/`, `/core/tools/log/`
- **Gateway:** `services/mcp_service` (FastAPI), `POST /mcp/call`
- **Tools e clients:** `app_mcp/tools/`, `app_mcp/clients/`

Aqui ficam:

- **`uri.py`** — Parser e validação de URIs `sinap://{vertical}/{entity}/{id}`
- **`resources/`** — Resolver de MCP Resources (get, list, search) usando adapters
- **Contratos** — Schemas compartilhados (Resources, URI)

Não movemos código existente; apenas adicionamos utilitários e convenções.

## URI sinap://

Formato: `sinap://{vertical}/{entity}/{id?}` ou `sinap://{vertical}/{entity}?query=...`

- **vertical:** vitrinezap | motopro | mrfoo | system
- **entity:** catalog | orders | menu | tools | logs | ...
- **id:** opcional (recurso específico)
- **query:** opcional (listagem/filtros)

Exemplos: `sinap://vitrinezap/catalog/123`, `sinap://system/tools`

## Prompts versionados

Convenção: `{vertical}/{purpose}/v{N}` (ex.: `vitrinezap/followup/v1`). O resolver em `app_mcp_tool_registry.utils` aceita refs antigas e essa convenção.
