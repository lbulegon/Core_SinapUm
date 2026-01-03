# Inventário MCP - Core_SinapUm

**Data:** 2025-01-27  
**Objetivo:** Mapear o que já existe, identificar duplicações e lacunas, e definir estratégia de convergência.

---

## 1. ESTRUTURA DO REPOSITÓRIO

### 1.1 Projeto Django Principal
- **Módulo:** `setup/`
  - `settings.py` - Configurações Django (linha 1-263)
  - `urls.py` - Roteamento principal (linha 1-77)
  - `wsgi.py` / `asgi.py` - Entry points
- **Apps Django instalados:**
  - `app_sinapum` - App principal (produtos, prompts, sistemas)
  - `app_mcp_tool_registry` - Registry de tools MCP
  - `app_ifood_integration` - Integração iFood

### 1.2 Apps Relacionados a MCP

#### A) `app_mcp_tool_registry/`
**Localização:** `/root/Core_SinapUm/app_mcp_tool_registry/`

**Models (`models.py`):**
- ✅ `ClientApp` - Aplicações cliente (key, name, api_key, is_active)
- ✅ `Tool` - Tool versionada (name, description, current_version FK, allowed_clients M2M)
- ✅ `ToolVersion` - Versão imutável (version, input_schema, output_schema, runtime, config, prompt_ref)
- ✅ `ToolCallLog` - Log de auditoria (request_id, trace_id, tool, version, client_key, ok, status_code, latency_ms, input_payload, output_payload, error_payload)

**Views (`views.py`):**
- ✅ `list_tools` - GET `/core/tools/` - Lista tools ativas
- ✅ `get_tool_detail` - GET `/core/tools/<tool_name>/` - Detalhes da tool
- ✅ `resolve_tool` - POST `/core/tools/resolve/` - Resolve tool e retorna execution_plan
- ✅ `log_tool_call` - POST `/core/tools/log/` - Registra log de execução

**Utils (`utils.py`):**
- ✅ `resolve_prompt_info` - Resolve prompt_ref (PostgreSQL, URL, inline)
- ✅ `resolve_prompt_from_ref` - Wrapper para obter texto do prompt

**URLs (`urls.py`):**
- ✅ `/core/tools/` - Lista tools
- ✅ `/core/tools/<tool_name>/` - Detalhes
- ✅ `/core/tools/resolve/` - Resolve tool
- ✅ `/core/tools/log/` - Log de chamada

**Status:** ✅ **COMPLETO** - Registry funcional com suporte a MCP-aware (context_pack, trace_id)

#### B) `app_sinapum/`
**Localização:** `/root/Core_SinapUm/app_sinapum/`

**Models (`models.py`):**
- ✅ `Sistema` - Sistemas/aplicativos (nome, codigo, ativo)
- ✅ `PromptTemplate` - Templates de prompts (sistema FK, nome, tipo_prompt, prompt_text, versao, ativo, parametros)
- ✅ `Produto`, `ProdutoJSON`, `CadastroMeta` - Models de domínio (não relacionados a MCP diretamente)

**Services (`services.py`):**
- ✅ `analyze_image_with_openmind` - Chama OpenMind para análise de imagem
- ✅ `analyze_multiple_images` - Análise múltipla
- Funções auxiliares de transformação

**Status:** ✅ **COMPLETO** - Suporte a prompts e sistemas, integração com OpenMind

### 1.3 Serviços (Data Plane)

#### A) `services/mcp_service/`
**Localização:** `/root/Core_SinapUm/services/mcp_service/`

**Arquitetura:** FastAPI (porta 7010)

**Funcionalidades (`main.py`):**
- ✅ Gateway MCP que consulta Core Registry (Django)
- ✅ Endpoint `/mcp/tools` - Lista tools (delega para Core)
- ✅ Endpoint `/mcp/call` - Executa tool (POST)
- ✅ Suporte a Context Pack (MCP-aware)
- ✅ Validação de schema (jsonschema)
- ✅ Execução de runtime (openmind_http, prompt, noop, pipeline, ddf)
- ✅ Logging no Core Registry (com trace_id e context_pack)
- ✅ Geração de request_id/trace_id se ausentes

**Runtimes implementados:**
- ✅ `openmind_http` - Chama OpenMind via HTTP
- ✅ `prompt` - Envia prompt para LLM via OpenMind
- ⚠️ `ddf` - Placeholder (não implementado)
- ⚠️ `pipeline` - Placeholder (não implementado)
- ✅ `noop` - No operation

**Status:** ✅ **COMPLETO** - Gateway funcional, mas runtime `ddf` não implementado (apenas placeholder)

#### B) `services/ddf_service/`
**Localização:** `/root/Core_SinapUm/services/ddf_service/`

**Arquitetura:** FastAPI (porta 8005 segundo docker-compose.yml)

**Estrutura:**
- `app/main.py` - Entrypoint FastAPI
- `app/api/` - Rotas
- `app/core/` - Lógica core
- `app/models/` - Models
- `app/providers/` - Providers de IA
- `app/mcp_tools/` - Tools MCP

**Docker Compose:** ✅ Existe (`docker-compose.yml`)

**Status:** ⚠️ **PARCIAL** - Serviço existe mas não está integrado ao Core como executor padrão. Precisa verificar se tem endpoint `/ddf/execute` e se está sendo usado pelo mcp_service.

#### C) `services/openmind_service/`
**Localização:** `/root/Core_SinapUm/services/ddf_service/`

**Arquitetura:** FastAPI (porta 8001 segundo docker-compose.yml)

**Status:** ✅ **EXISTE** - Serviço de IA (OpenMind) usado pelo mcp_service

### 1.4 Docker Compose

**Principal:** `/root/Core_SinapUm/docker-compose.yml`
- ✅ `db` - PostgreSQL (porta 5432)
- ✅ `openmind` - OpenMind Service (porta 8001)
- ✅ `web` - Django Core (porta 5000)
- ✅ `ifood_service` - iFood Service (porta 7020)
- ⚠️ **FALTA:** `mcp_service` (porta 7010)
- ⚠️ **FALTA:** `ddf_service` (porta 8005 ou 8010)

**Serviços individuais:**
- ✅ `services/mcp_service/docker-compose.yml` - Existe mas isolado
- ✅ `services/ddf_service/docker-compose.yml` - Existe mas isolado

**Status:** ⚠️ **PARCIAL** - Serviços não estão no compose principal

### 1.5 Dependências

**Arquivo:** `/root/Core_SinapUm/requirements.txt`

**Bibliotecas relevantes:**
- ✅ `jsonschema==4.25.1` - Validação de schemas
- ✅ `httpx==0.28.1` - HTTP client (mas mcp_service usa `requests`)
- ✅ `requests==2.32.5` - HTTP client usado
- ✅ `Django==4.2.27` - Framework Django
- ✅ `psycopg2-binary==2.9.9` - PostgreSQL driver

**Status:** ✅ **COMPLETO** - Dependências necessárias presentes

---

## 2. IMPLEMENTAÇÕES EXISTENTES

### 2.1 Registry de Tools
✅ **EXISTE E ESTÁ COMPLETO**
- **Localização:** `app_mcp_tool_registry/models.py`
- **Entidades:** Tool, ToolVersion, ClientApp, ToolCallLog
- **Funcionalidades:**
  - Versionamento de tools
  - Schemas de input/output
  - Runtime configurável
  - Permissões por cliente (allowed_clients)
  - Logs de auditoria com trace_id

### 2.2 Dispatcher/Executor
⚠️ **EXISTE MAS NÃO ESTÁ UNIFICADO**
- **Localização:** `services/mcp_service/main.py`
- **Função:** `execute_runtime()` - Executa runtime baseado em tipo
- **Problema:** Dispatcher está no mcp_service (FastAPI), não no Core (Django)
- **Runtimes suportados:**
  - ✅ `openmind_http` - Implementado
  - ✅ `prompt` - Implementado
  - ⚠️ `ddf` - Placeholder apenas
  - ⚠️ `pipeline` - Placeholder apenas

**Falta:** Dispatcher unificado no Core Django que possa ser chamado diretamente

### 2.3 Endpoints de API

#### Core Django (`app_mcp_tool_registry/urls.py`):
- ✅ GET `/core/tools/` - Lista tools
- ✅ GET `/core/tools/<tool_name>/` - Detalhes
- ✅ POST `/core/tools/resolve/` - Resolve tool
- ✅ POST `/core/tools/log/` - Log de chamada
- ❌ **FALTA:** POST `/core/tools/<id>/execute/` - Executar tool diretamente no Core

#### MCP Service (`services/mcp_service/main.py`):
- ✅ GET `/mcp/tools` - Lista tools (delega para Core)
- ✅ POST `/mcp/call` - Executa tool
- ✅ GET `/health` - Health check

**Status:** ⚠️ **PARCIAL** - Falta endpoint de execução direta no Core

### 2.4 Autenticação

**Implementado:**
- ✅ API Key via header `X-SINAPUM-KEY`
- ✅ Model `ClientApp` com `api_key`
- ✅ Validação em `get_client_from_api_key()` (views.py)

**Falta:**
- ❌ Header alternativo `X-MCP-KEY` (mencionado no requisito)
- ❌ Scopes/permissões granulares (apenas allowed_clients M2M)

**Status:** ✅ **BÁSICO** - Funciona mas pode ser melhorado

### 2.5 Auditoria/Logs

✅ **EXISTE E ESTÁ COMPLETO**
- **Model:** `ToolCallLog` em `app_mcp_tool_registry/models.py`
- **Campos:** request_id, trace_id, tool, version, client_key, ok, status_code, latency_ms, input_payload, output_payload, error_payload
- **Endpoint:** POST `/core/tools/log/`
- **Integração:** mcp_service registra logs automaticamente

**Status:** ✅ **COMPLETO** - Sistema de auditoria funcional

### 2.6 Validação de Schema

✅ **EXISTE**
- **Biblioteca:** `jsonschema` (já instalada)
- **Uso:** `validate_json_schema()` em `mcp_service/main.py`
- **Aplicação:** Valida input_schema antes de executar, valida output_schema após (não crítico)

**Falta:**
- ❌ Limite de tamanho de input (`MCP_MAX_INPUT_BYTES`)
- ❌ Validação no Core Django (apenas no mcp_service)

**Status:** ⚠️ **PARCIAL** - Funciona mas falta limite de tamanho

### 2.7 Correlation ID / Trace ID

✅ **EXISTE**
- **Campo:** `trace_id` em `ToolCallLog` e `ContextPack`
- **Geração:** Automática se ausente em `normalize_context_pack()`
- **Propagação:** Incluído em logs e responses

**Status:** ✅ **COMPLETO** - Sistema de rastreamento funcional

---

## 3. DUPLICAÇÕES E LACUNAS

### 3.1 Duplicações

1. **Dispatcher em dois lugares:**
   - ❌ `services/mcp_service/main.py` - `execute_runtime()`
   - ❌ **FALTA:** Dispatcher no Core Django
   - **Decisão:** Criar dispatcher unificado no Core, mcp_service delega para Core

2. **Validação de schema:**
   - ✅ Apenas no mcp_service
   - ❌ **FALTA:** No Core Django
   - **Decisão:** Adicionar validação no Core também

### 3.2 Lacunas

1. **Endpoint de execução direta no Core:**
   - ❌ POST `/core/tools/<id>/execute/` ou `/mcp/tools/<id>/execute/`
   - **Decisão:** Criar endpoint no Core que chama dispatcher interno

2. **Runtime DDF não implementado:**
   - ⚠️ Placeholder em `mcp_service/main.py`
   - ✅ DDF service existe mas não está integrado
   - **Decisão:** Integrar DDF service como executor padrão quando runtime=ddf

3. **Limite de tamanho de input:**
   - ❌ `MCP_MAX_INPUT_BYTES` não existe
   - **Decisão:** Adicionar validação de tamanho no dispatcher

4. **Docker Compose principal:**
   - ❌ `mcp_service` não está no compose principal
   - ❌ `ddf_service` não está no compose principal
   - **Decisão:** Adicionar serviços ao compose principal

5. **Endpoint de listagem de execuções:**
   - ❌ GET `/mcp/executions/` ou `/core/executions/`
   - **Decisão:** Criar endpoint para listar logs de execução

6. **Scopes/permissões granulares:**
   - ⚠️ Apenas allowed_clients M2M
   - **Decisão:** Manter simples por enquanto, adicionar scopes se necessário

---

## 4. DECISÕES DE CONVERGÊNCIA

### 4.1 Source of Truth (Django Core)

✅ **REUTILIZAR:**
- `app_mcp_tool_registry/models.py` - Todos os models estão corretos
- `Tool`, `ToolVersion`, `ToolCallLog`, `ClientApp` - Não precisam mudança

✅ **COMPLEMENTAR:**
- Adicionar campo `correlation_id` como alias de `request_id` (opcional, manter compatibilidade)
- Adicionar método `execute_tool()` no Core Django

### 4.2 Dispatcher Único

✅ **CRIAR:**
- `app_mcp_tool_registry/services.py` ou `app_mcp_tool_registry/dispatcher.py`
- Função `execute_tool(tool_name, version, input_data, client_key, context_pack=None)`
- Validação de schema (jsonschema)
- Limite de tamanho de input (`MCP_MAX_INPUT_BYTES`)
- Geração de correlation_id/request_id
- Logging sempre (success/error)
- Roteamento por runtime: openmind | ddf | http

✅ **ADAPTAR:**
- `mcp_service/main.py` - Fazer dele chamar Core Django via HTTP ou manter lógica local (decisão arquitetural)

### 4.3 Rotas (API)

✅ **MANTER:**
- GET `/core/tools/` - Lista tools
- GET `/core/tools/<tool_name>/` - Detalhes
- POST `/core/tools/resolve/` - Resolve tool
- POST `/core/tools/log/` - Log de chamada

✅ **ADICIONAR:**
- POST `/core/tools/<tool_name>/execute/` - Executa tool diretamente no Core
- GET `/core/executions/` - Lista logs de execução (com filtros opcionais)

✅ **MANTER COMPATIBILIDADE:**
- `/mcp/call` no mcp_service continua funcionando (delega para Core ou executa localmente)

### 4.4 Auth

✅ **MANTER:**
- Header `X-SINAPUM-KEY` (existente)

✅ **ADICIONAR:**
- Header alternativo `X-MCP-KEY` (alias para X-SINAPUM-KEY)
- Manter compatibilidade com ambos

✅ **NÃO CRIAR:**
- Scopes granulares por enquanto (allowed_clients M2M é suficiente)

### 4.5 DDF Service

✅ **VERIFICAR:**
- Se DDF service tem endpoint `/ddf/execute`
- Se está configurado para receber jobs do Core

✅ **INTEGRAR:**
- Se não existir endpoint `/ddf/execute`, criar
- Configurar DDF_BASE_URL no Core
- Runtime `ddf` no dispatcher chama DDF service

✅ **NÃO DUPLICAR:**
- DDF service já existe, apenas integrar

---

## 5. PLANO DE IMPLEMENTAÇÃO

### FASE 2 - Convergência (Prioridade)

#### 2.1 Dispatcher no Core Django
- [ ] Criar `app_mcp_tool_registry/services.py` ou `dispatcher.py`
- [ ] Implementar `execute_tool()` com:
  - Validação de schema
  - Limite de tamanho de input
  - Geração de correlation_id
  - Logging sempre
  - Roteamento por runtime

#### 2.2 Endpoint de Execução no Core
- [ ] Criar view `execute_tool_view` em `app_mcp_tool_registry/views.py`
- [ ] Adicionar rota POST `/core/tools/<tool_name>/execute/`
- [ ] Integrar com dispatcher

#### 2.3 Endpoint de Listagem de Execuções
- [ ] Criar view `list_executions` em `app_mcp_tool_registry/views.py`
- [ ] Adicionar rota GET `/core/executions/`
- [ ] Suportar filtros (tool, client_key, date_range, etc.)

#### 2.4 Validação e Limites
- [ ] Adicionar `MCP_MAX_INPUT_BYTES` em settings.py
- [ ] Validar tamanho de input no dispatcher
- [ ] Truncar payloads grandes nos logs

#### 2.5 Auth Melhorado
- [ ] Adicionar suporte a `X-MCP-KEY` (alias de X-SINAPUM-KEY)
- [ ] Manter compatibilidade

#### 2.6 Docker Compose
- [ ] Adicionar `mcp_service` ao docker-compose.yml principal
- [ ] Adicionar `ddf_service` ao docker-compose.yml principal (se necessário)
- [ ] Configurar variáveis de ambiente

### FASE 3 - DDF Service (Se necessário)

#### 3.1 Verificar DDF Service
- [ ] Verificar se tem endpoint `/ddf/execute`
- [ ] Verificar se está configurado corretamente

#### 3.2 Integrar DDF
- [ ] Adicionar `DDF_BASE_URL` em settings.py
- [ ] Implementar runtime `ddf` no dispatcher
- [ ] Testar integração

---

## 6. RESUMO EXECUTIVO

### O que já existe e está completo:
1. ✅ Registry de tools (Tool, ToolVersion, ClientApp, ToolCallLog)
2. ✅ Endpoints de registry (list, detail, resolve, log)
3. ✅ Sistema de auditoria (ToolCallLog com trace_id)
4. ✅ MCP Service como gateway
5. ✅ Suporte a Context Pack (MCP-aware)
6. ✅ Validação de schema (jsonschema)
7. ✅ Correlation ID / Trace ID

### O que precisa ser criado/complementado:
1. ❌ Dispatcher unificado no Core Django
2. ❌ Endpoint de execução direta no Core
3. ❌ Endpoint de listagem de execuções
4. ❌ Limite de tamanho de input (MCP_MAX_INPUT_BYTES)
5. ❌ Integração do runtime DDF
6. ❌ Serviços no docker-compose principal
7. ❌ Header alternativo X-MCP-KEY

### O que precisa ser refatorado:
1. ⚠️ Mover lógica de execução do mcp_service para Core (ou manter delegando)
2. ⚠️ Adicionar validação de tamanho de input

### Decisões arquiteturais pendentes:
1. **Dispatcher:** Manter no mcp_service (FastAPI) ou mover para Core (Django)?
   - **Recomendação:** Criar dispatcher no Core, mcp_service delega via HTTP
   - **Alternativa:** Manter dispatcher no mcp_service, Core apenas registry

2. **DDF Service:** Integrar como serviço padrão ou manter isolado?
   - **Recomendação:** Integrar como executor quando runtime=ddf

---

## 7. PRÓXIMOS PASSOS

1. ✅ **INVENTÁRIO COMPLETO** (este documento)
2. ✅ **IMPLEMENTAR FASE 2** - Convergência (CONCLUÍDO)
3. ✅ **VERIFICAR FASE 3** - DDF Service (INTEGRADO)
4. ⏭️ **TESTES** - Garantir compatibilidade

---

## 8. IMPLEMENTAÇÃO REALIZADA (2025-01-27)

### 8.1 Dispatcher Unificado no Core Django
✅ **CRIADO:** `app_mcp_tool_registry/services.py`
- Função `execute_tool()` - Dispatcher principal
- Validação de tamanho de input (`MCP_MAX_INPUT_BYTES`)
- Validação de schema (jsonschema)
- Geração automática de request_id/trace_id
- Logging sempre (success/error)
- Runtimes implementados:
  - ✅ `openmind_http` - Chama OpenMind via HTTP
  - ✅ `prompt` - Envia prompt para LLM via OpenMind
  - ✅ `ddf` - Delega para DDF Service (INTEGRADO)
  - ✅ `noop` - No operation
  - ⚠️ `pipeline` - Placeholder (não implementado)

### 8.2 Endpoints Adicionados
✅ **POST `/core/tools/<tool_name>/execute/`**
- Executa tool diretamente no Core Django
- Suporta headers `X-SINAPUM-KEY` e `X-MCP-KEY`
- Retorna resultado padronizado com request_id/trace_id

✅ **GET `/core/executions/`**
- Lista logs de execução (auditoria)
- Suporta filtros: tool, client_key, ok, limit, offset
- Retorna logs com paginação

### 8.3 Configurações Adicionadas
✅ **settings.py:**
- `MCP_MAX_INPUT_BYTES` - Limite de tamanho de input (padrão: 10MB)
- `DDF_BASE_URL` - URL do DDF Service (padrão: http://ddf_service:8005)
- `DDF_TIMEOUT` - Timeout para chamadas DDF (padrão: 60s)
- `MCP_SERVICE_URL` - URL do MCP Service (para referência)

### 8.4 Autenticação Melhorada
✅ **Suporte a `X-MCP-KEY`:**
- Header alternativo para `X-SINAPUM-KEY`
- Compatibilidade mantida com ambos
- Função `get_client_from_api_key()` atualizada

### 8.5 Docker Compose
✅ **Serviços adicionados ao compose principal:**
- `mcp_service` - Porta 7010
- `ddf_service` - Porta 8005
- `ddf_redis` - Porta 6380
- `ddf_postgres` - Porta 5434
- Volumes adicionados: `ddf_storage`, `ddf_redis_data`, `ddf_postgres_data`

### 8.6 Integração DDF
✅ **Runtime DDF implementado:**
- Função `execute_runtime_ddf()` em `services.py`
- Adapta input para formato esperado pelo DDF (`text`, `context`, `params`)
- Suporta provider override via config
- Integrado ao dispatcher principal

---

## 9. STATUS FINAL

### ✅ Implementado e Funcional:
1. Dispatcher unificado no Core Django
2. Endpoint de execução direta no Core
3. Endpoint de listagem de execuções
4. Validação de tamanho de input
5. Suporte a header X-MCP-KEY
6. Integração do runtime DDF
7. Serviços no docker-compose principal

### ⚠️ Pendente (Opcional):
1. Runtime `pipeline` (não implementado, apenas placeholder)
2. Scopes/permissões granulares (mantido simples com allowed_clients M2M)
3. Testes automatizados (recomendado adicionar)

### 📝 Notas:
- **Compatibilidade:** Todos os endpoints existentes continuam funcionando
- **Breaking Changes:** Nenhum
- **Migrações:** Não necessárias (apenas código novo)

---

**Fim do Inventário**

