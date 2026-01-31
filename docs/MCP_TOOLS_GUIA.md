# Guia das Tools MCP - Core_SinapUm

## 1. Visão Geral

O Core_SinapUm expõe tools MCP em dois pontos:

| Ponto | Rota | Descrição |
|-------|------|-----------|
| **MCP Service** | `POST http://mcp_service:7010/mcp/call` | Gateway para tools versionadas (Tool Registry) |
| **app_mcp** | `POST http://web:5000/mcp/tools/<name>` | Tools VitrineZap (cart, catalog, order) |

---

## 2. MCP Service (porta 7010)

### Tools versionadas (Tool Registry)

**Exemplo: vitrinezap.analisar_produto**

```bash
curl -X POST http://localhost:7010/mcp/call \
  -H "Content-Type: application/json" \
  -H "X-SINAPUM-KEY: <api_key>" \
  -d '{
    "tool": "vitrinezap.analisar_produto",
    "version": "1.0.0",
    "input": {
      "image_url": "https://exemplo.com/produto.jpg",
      "prompt_params": {}
    }
  }'
```

**Com imagem em base64:**

```json
{
  "tool": "vitrinezap.analisar_produto",
  "input": {
    "image_base64": "<base64 da imagem>",
    "prompt_params": {}
  }
}
```

**Response:**
```json
{
  "request_id": "uuid",
  "trace_id": "uuid",
  "tool": "vitrinezap.analisar_produto",
  "version": "1.0.0",
  "ok": true,
  "output": {
    "success": true,
    "data": { "produto": {...}, "cadastro_meta": {...} }
  },
  "latency_ms": 2500
}
```

### Tool: sparkscore.analisar_peca

Analisa peça criativa (texto, imagem) via SparkScore - orbitais semiótico, emocional, CSV, etc.

```bash
curl -X POST http://localhost:7010/mcp/call \
  -H "Content-Type: application/json" \
  -H "X-SINAPUM-KEY: <api_key>" \
  -d '{
    "tool": "sparkscore.analisar_peca",
    "input": {
      "piece_id": "peca_001",
      "piece_type": "text",
      "text_overlay": "PROMO - Chame no WhatsApp",
      "caption": "Compartilhe",
      "objective": {"primary_goal": "whatsapp_click"},
      "distribution": {"channel": "whatsapp_status", "format": "story_vertical"}
    }
  }'
```

### Listar tools disponíveis

```bash
curl http://localhost:7010/mcp/tools
```

---

## 3. app_mcp - Tools VitrineZap (porta 5000)

**Requisito:** `FEATURE_EVOLUTION_MULTI_TENANT=true` no Core.

### Tools disponíveis

| Tool | Descrição | Args |
|------|-----------|------|
| `customer.get_or_create` | Obtém ou cria cliente | `phone` |
| `catalog.search` | Busca no catálogo | `query`, `filters` |
| `product.get` | Obtém produto por ID | `product_id` |
| `cart.get` | Obtém carrinho | `customer_id` |
| `cart.add` | Adiciona ao carrinho | `customer_id`, `product_id`, `quantity` |
| `order.create` | Cria pedido | `customer_id`, `cart_id`, `address`, `payment_method` |
| `order.status` | Status do pedido | `order_id` |

### Exemplo: catalog.search

```bash
curl -X POST http://localhost:5000/mcp/tools/catalog.search \
  -H "Content-Type: application/json" \
  -d '{
    "shopper_id": "shopper-uuid",
    "args": {
      "query": "arroz",
      "filters": {}
    }
  }'
```

### Exemplo: cart.add

```bash
curl -X POST http://localhost:5000/mcp/tools/cart.add \
  -H "Content-Type: application/json" \
  -d '{
    "shopper_id": "shopper-uuid",
    "args": {
      "customer_id": "customer-123",
      "product_id": "prod-456",
      "quantity": 2
    }
  }'
```

---

## 4. ShopperBot como proxy MCP

O ShopperBot (porta 7030) pode chamar as tools app_mcp em nome do cliente:

```bash
# Listar tools
curl http://localhost:7030/v1/mcp/tools

# Chamar tool
curl -X POST http://localhost:7030/v1/mcp/call \
  -H "Content-Type: application/json" \
  -d '{
    "tool_name": "catalog.search",
    "shopper_id": "shopper-uuid",
    "args": {"query": "arroz"}
  }'
```

**Variáveis de ambiente ShopperBot:**
- `MCP_CORE_URL`: URL do Core (default: `http://web:5000`)
- `MCP_ENABLED`: `true`/`false` (default: `true`)

---

## 5. Execução direta no Core

Para executar tools do Registry diretamente no Django (sem MCP Service):

```bash
curl -X POST http://localhost:5000/core/tools/vitrinezap.analisar_produto/execute/ \
  -H "Content-Type: application/json" \
  -H "X-SINAPUM-KEY: <api_key>" \
  -d '{
    "input": {
      "image_url": "https://exemplo.com/produto.jpg"
    },
    "client_key": "vitrinezap"
  }'
```

---

## 6. Unificação /analyze/ com MCP

O endpoint `/analyze/` e `/api/v1/analyze-product-image` usam MCP quando:

- `USE_MCP_FOR_ANALYZE=true` (default)
- A tool `vitrinezap.analisar_produto` está registrada e ativa

Se a tool não existir ou falhar, o fluxo faz fallback para OpenMind direto.

**Desabilitar MCP para análise:**
```bash
export USE_MCP_FOR_ANALYZE=false
```

---

## 7. DDF como servidor MCP

O DDF expõe tools via HTTP REST em formato MCP-compatível:

```bash
# Listar tools
curl http://localhost:8005/ddf/mcp/tools

# Chamar ddf_detect
curl -X POST http://localhost:8005/ddf/mcp/call \
  -H "Content-Type: application/json" \
  -d '{"tool": "ddf_detect", "arguments": {"text": "escreva um poema"}}'

# Chamar ddf_list_categories
curl -X POST http://localhost:8005/ddf/mcp/call \
  -H "Content-Type: application/json" \
  -d '{"tool": "ddf_list_categories", "arguments": {}}'
```

## 8. MCP nativo (stdio)

Para usar com Claude Desktop ou Cursor como servidor MCP local:

```bash
cd services/mcp_service
pip install mcp requests
MCP_SERVICE_URL=http://localhost:7010 python run_mcp_stdio.py
```

Configuração no Claude Desktop (`claude_desktop_config.json`):

```json
{
  "mcpServers": {
    "sinapum": {
      "command": "python",
      "args": ["/caminho/para/Core_SinapUm/services/mcp_service/run_mcp_stdio.py"],
      "env": {
        "MCP_SERVICE_URL": "http://localhost:7010",
        "SINAPUM_API_KEY": "sua-api-key"
      }
    }
  }
}
```

## 9. Referências

- `docs/MCP_ATUACAO_E_MELHORIAS.md` – Atuação e melhorias
- `docs/INVENTARIO_MCP.md` – Inventário técnico
- `services/mcp_service/README.md` – MCP Service
- `register_vitrinezap_tool.py` – Registro da tool de análise
