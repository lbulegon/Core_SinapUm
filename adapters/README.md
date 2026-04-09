# Adapters — camada entre MCP e serviços existentes

Cada adapter expõe funções estáveis e delega para clients/endpoints/serviços já existentes. Tools MCP e handlers de Resources sinap:// usam adapters (não duplicam lógica).

## Módulos

- **vitrinezap_adapter** — catálogo, pedidos, carrinho, cliente (VitrineZapClient).
- **motopro_adapter** — pedidos, slots, rotas (stub).
- **mrfoo_adapter** — cardápio, lista de compras (stub).
- **openmind_adapter** — análise de imagens/LLM (stub).
- **ifood_adapter** — pedidos iFood (stub).
- **ddf_adapter** — DDF (stub).

## Resources (sinap://)

Handlers registrados em `register_resources.register_all_resource_handlers()` (chamado no `app_mcp_tool_registry.apps.ready()`):

- `sinap://vitrinezap/catalog/{id}` — get/list via VitrineZapAdapter.
- `sinap://vitrinezap/orders/{id}` — get via VitrineZapAdapter.
- `sinap://motopro/orders/{id}` — get (stub).
- `sinap://mrfoo/menu/{id}` — get (stub).

Query opcional: `shopper_id`, `q`, `limit` (ex.: `sinap://vitrinezap/catalog/123?shopper_id=xxx`).

## Compatibilidade

- Assinaturas das tools em `app_mcp/tools` foram mantidas; apenas passam a chamar adapters.
- Clients existentes (VitrineZapClient) continuam sendo usados dentro do adapter.
