# MCP no Core_SinapUm: Atuação e Melhorias

**Data:** 2025-01-30  
**Objetivo:** Clarear como o MCP é usado no projeto e propor melhorias.

---

## 1. O que é MCP no contexto SinapUm?

**Model Context Protocol (MCP)** aqui se refere a:

1. **MCP Service** – Gateway FastAPI (porta 7010) que expõe tools versionadas
2. **MCP Tool Registry** – Registry no Django (banco de dados) de tools, versões e clients
3. **app_mcp** – Conjunto de tools VitrineZap (cart, catalog, order) no Django

---

## 2. Componentes e responsabilidades

### 2.1 MCP Service (porta 7010)

| Aspecto | Descrição |
|---------|-----------|
| **O que faz** | Gateway que recebe chamadas de tools e delega execução |
| **Fluxo** | Cliente → POST /mcp/call → Resolve no Core → Executa runtime → Retorna |
| **Dependências** | Core (Django 5000) para resolve, OpenMind (8001) para openmind_http |
| **Runtimes** | openmind_http, prompt, ddf, noop |

**Fluxo típico (vitrinezap.analisar_produto):**
```
Cliente (ex: Cursor, Claude Code, app externo)
    → POST http://mcp_service:7010/mcp/call
    → MCP Service chama Core: POST /core/tools/resolve
    → Core retorna execution_plan (runtime=openmind_http, config, prompt_ref)
    → MCP Service executa: POST OpenMind /api/v1/analyze-product-image
    → MCP Service registra log: POST /core/tools/log
    → Retorna output ao cliente
```

### 2.2 MCP Tool Registry (Django /core/)

| Endpoint | Descrição |
|----------|-----------|
| GET /core/tools/ | Lista tools disponíveis |
| GET /core/tools/\<name\>/ | Detalhes de uma tool |
| POST /core/tools/resolve/ | Resolve tool → execution_plan |
| POST /core/tools/\<name\>/execute/ | Executa tool diretamente (dispatcher no Core) |
| POST /core/tools/log/ | Registra chamada (auditoria) |
| GET /core/executions/ | Lista logs de execução |

**Models:** ClientApp, Tool, ToolVersion, ToolCallLog

### 2.3 app_mcp (Django /mcp/)

| Aspecto | Descrição |
|---------|-----------|
| **Quando ativo** | Apenas se `FEATURE_EVOLUTION_MULTI_TENANT=true` |
| **Endpoint** | POST /mcp/tools/\<tool_name\> |
| **Tools** | customer.get_or_create, catalog.search, product.get, cart.get, cart.add, order.create, order.status |
| **Formato** | `{shopper_id, args}` – não usa Tool Registry |
| **Uso** | Tools VitrineZap para IA/ShopperBot operar carrinho, catálogo, pedidos |

**Importante:** app_mcp é um conjunto **fixo** de tools, **independente** do MCP Service e do Tool Registry.

### 2.4 Quem chama o quê

| Chamador | Usa MCP Service? | Usa Tool Registry? | Usa app_mcp? |
|----------|------------------|--------------------|--------------|
| Cursor / Claude Code | Sim (via /mcp/call) | Sim (via resolve) | Não |
| OpenMind (análise imagem) | Pode sim | Pode sim | Não |
| Endpoint /analyze/ (Django) | **Não** | **Não** | Não |
| ShopperBot / IA vendedora | Não (ainda) | Não | Sim (quando FEATURE on) |

**Lacuna conhecida:** O endpoint `/analyze/` (views do app_sinapum) usa `analyze_image_with_openmind` direto, **sem passar pelo MCP Service**. Portanto não usa a tool `vitrinezap.analisar_produto` nem o prompt versionado do Tool Registry.

---

## 3. Diagrama de fluxo atual

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         CLIENTES EXTERNOS                                │
│  (Cursor, Claude Code, CUSTOM_APP, etc.)                                 │
└───────────────────────────────┬─────────────────────────────────────────┘
                                │ POST /mcp/call
                                ▼
┌─────────────────────────────────────────────────────────────────────────┐
│  MCP Service (7010)                                                      │
│  - Resolve tool no Core                                                  │
│  - Valida schema                                                         │
│  - Executa runtime (openmind_http, ddf, etc.)                           │
│  - Registra log                                                          │
└───────────┬─────────────────────────────────┬───────────────────────────┘
            │                                 │
            │ resolve / log                   │ openmind_http
            ▼                                 ▼
┌───────────────────────┐         ┌───────────────────────────────────────┐
│  Core Django (5000)   │         │  OpenMind (8001)                       │
│  - /core/tools/       │         │  - /api/v1/analyze-product-image       │
│  - Tool Registry      │         │  - Análise de imagens com IA           │
│  - Dispatcher         │         └───────────────────────────────────────┘
└───────────────────────┘

┌─────────────────────────────────────────────────────────────────────────┐
│  FLUXO PARALELO (legado) – NÃO USA MCP                                   │
│  /analyze/ → analyze_image_with_openmind() → OpenMind direto             │
│  (Prompt do PostgreSQL PromptTemplate, não do Tool Registry)             │
└─────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────┐
│  app_mcp (Django /mcp/) – Tools VitrineZap                               │
│  POST /mcp/tools/cart.add, catalog.search, etc.                          │
│  Usado por: ShopperBot / IA (quando FEATURE_EVOLUTION_MULTI_TENANT)      │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## 4. Melhorias propostas

### 4.1 Curto prazo

| Melhoria | Descrição | Impacto |
|----------|-----------|---------|
| **Unificar /analyze/** | Fazer `/analyze/` usar MCP Service ou Core execute, para centralizar prompt no Tool Registry | Consistência, versionamento único |
| **Integrar ShopperBot** | ShopperBot chamar app_mcp ou MCP Service para cart/catalog/order | IA vendedora com ações reais |
| **Documentar tools** | README com lista de tools, exemplos de chamada, schemas | Onboarding, integrações |
| **Testes MCP** | Testes de integração para /mcp/call e /core/tools/execute | Regressão, confiabilidade |

### 4.2 Médio prazo

| Melhoria | Descrição | Impacto |
|----------|-----------|---------|
| **Unificar app_mcp e Registry** | Migrar tools do app_mcp para o Tool Registry, MCP Service como único gateway | Uma única API de tools |
| **Runtime SparkScore** | Adicionar runtime `sparkscore` no MCP para análise de peças | SparkScore acessível como tool |
| **Webhook/Eventos** | Tool para disparar eventos (ex: pedido criado → webhook) | Integrações assíncronas |
| **Dashboard de execuções** | UI para ver ToolCallLog, filtros, métricas | Operação, debugging |

### 4.3 Longo prazo

| Melhoria | Descrição | Impacto |
|----------|-----------|---------|
| **DDF como servidor MCP** | DDF expor tools (detect, delegate, execute) via MCP | Claude Code usa DDF direto |
| **MCP nativo (stdio/SSE)** | Suportar protocolo MCP completo (não só HTTP) | Compatibilidade com ecossistema MCP |
| **Scopes por tool** | Permissões granulares (ex: tool X só para client Y) | Segurança, multi-tenant |

---

## 5. Melhorias implementadas (2025-01-30)

### Curto prazo ✅
- [x] **Unificar /analyze/ com MCP** – `USE_MCP_FOR_ANALYZE=true` usa vitrinezap.analisar_produto quando registrada; fallback para OpenMind direto
- [x] **Integrar ShopperBot com app_mcp** – ShopperBot expõe `/v1/mcp/call` e `/v1/mcp/tools`; MCP_CORE_URL e MCP_ENABLED configuráveis
- [x] **Documentar tools** – `docs/MCP_TOOLS_GUIA.md` com exemplos e schemas
- [x] **Testes de integração MCP** – `tests/integration/test_mcp_full.py`

### Longo prazo ✅
- [x] **DDF como servidor MCP** – Endpoints `/ddf/mcp/tools` e `/ddf/mcp/call` no DDF Service
- [x] **Suporte MCP nativo (stdio)** – Script `services/mcp_service/run_mcp_stdio.py` para Claude Desktop / Cursor

## 6. Checklist de ação imediata

- [ ] Confirmar quem usa MCP Service hoje (clientes, integrações)
- [x] Decidir: unificar `/analyze/` com MCP ou manter legado? **→ Implementado com fallback**
- [ ] Habilitar `FEATURE_EVOLUTION_MULTI_TENANT` em prod? (para app_mcp)
- [x] Adicionar testes de integração para MCP
- [x] Documentar exemplos de chamada em README

---

## 7. Referências

- `docs/INVENTARIO_MCP.md` – Inventário técnico completo
- `docs/MCP_INTEGRATION.md` – Integração MCP com DDF
- `services/mcp_service/README.md` – MCP Service
- `register_vitrinezap_tool.py` – Registro da tool vitrinezap.analisar_produto
