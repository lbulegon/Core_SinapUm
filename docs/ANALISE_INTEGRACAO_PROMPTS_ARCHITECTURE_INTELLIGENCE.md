# Análise: Integração do Sistema de Prompts ao Architecture Intelligence

## 1. Estrutura atual do sistema de Prompts no Core_SinapUm

### 1.1 Camadas identificadas

| Camada | Localização | Função |
|--------|-------------|--------|
| **Documentação / Governança** | `prompts/` (raiz) | `00_prompt_dos_prompts.md`, `01_regras_gerais.md`, `tipos/`, `vitrinezap/` — critérios, tipos (análise, curadoria, decisão), regras. **Não é runtime.** |
| **PostgreSQL (PromptTemplate)** | `app_sinapum.models.PromptTemplate` | Armazena prompts versionados: sistema, nome, tipo_prompt, prompt_text, versao, ativo, parametros. Usado por MCP Tool Registry. |
| **Resolução (prompt_ref)** | `app_mcp_tool_registry.utils` | `resolve_prompt_info()`, `resolve_prompt_from_ref()` — resolve referência para texto. Fontes: PostgreSQL, URL, inline. |
| **ToolVersion.prompt_ref** | `app_mcp_tool_registry.models` | Campo que referencia prompt (nome, sistema:nome, URL). Usado na execução de tools. |

### 1.2 Formatos de prompt_ref suportados

- **Nome simples:** `analise_produto_v1`
- **Sistema:nome:** `evora:analise_produto_v1`
- **Vertical/purpose/vN:** `vitrinezap/followup/v1`
- **URL:** `https://...`
- **Inline:** `config.prompt_inline` (prioridade sobre prompt_ref)

### 1.3 Architecture Intelligence — estado atual

| Aspecto | Situação |
|---------|----------|
| **Prompts** | Arquivos `.md` em `services/architecture_intelligence_service/app/prompts/` |
| **Carregamento** | `StageExecutor._load_prompt()` lê do disco por role (chief_architect, architecture_review_board, etc.) |
| **Integração** | **Nenhuma** — não usa PromptTemplate nem prompt_ref |
| **Endpoint /evaluate** | Lê `architecture_intelligence_engine.md` direto do Path |

---

## 2. Esforço de integração — cenários

### Cenário A: Architecture Intelligence usar prompt_ref (via adapter Django)

**Ideia:** O adapter em `app_architecture_intelligence/services.py` resolve os prompts via `resolve_prompt_from_ref` e envia o texto no payload para o architecture_intelligence_service.

**Problema:** O service FastAPI executa os stages internamente; o adapter só chama cycle/start e run_stage. O service carrega os prompts dentro do StageExecutor. Para usar prompt_ref, seria preciso:

1. **Opção A1 — Service aceitar prompts injetados:** Novo parâmetro no payload (ex: `prompts_override: { "chief_architect": "...", ... }`). Se presente, o service usa em vez de carregar do disco.
2. **Opção A2 — Endpoint no Core para resolver:** O adapter chama um endpoint Django que retorna os prompts resolvidos; o adapter monta o payload com prompts_override.

**Esforço estimado:** 2–3 dias  
- Alterar schemas e rotas do architecture_intelligence_service (A1)  
- Ou criar endpoint no Core + adapter (A2)  
- Cadastrar prompts no PromptTemplate (seed)  
- Testes

---

### Cenário B: Migrar prompts do Architecture Intelligence para PromptTemplate

**Ideia:** Cadastrar os 7 prompts (chief_architect, architecture_review_board, etc.) no PostgreSQL. O service passa a buscar de uma API do Core em vez de arquivos .md.

**Problema:** O architecture_intelligence_service é FastAPI e não tem acesso ao Django. Precisaria:

1. API no Core: `GET /api/prompts/resolve?ref=architecture_intelligence:chief_architect_v1`
2. Ou: o service chamar o Core (HTTP) para resolver prompt_ref
3. Criar Sistema "architecture_intelligence" e cadastrar os 7 prompts

**Esforço estimado:** 3–4 dias  
- API de resolução de prompts no Core  
- Service configurável para usar API de prompts (env)  
- Migration/seed dos prompts  
- Fallback para arquivos .md se API indisponível

---

### Cenário C: Sincronização bidirecional (arquivos ↔ PromptTemplate)

**Ideia:** Manter os .md como fonte, com script que popula/atualiza o PromptTemplate. Permite edição via Admin e versionamento.

**Esforço estimado:** 2 dias  
- Script `sync_architecture_prompts_to_db.py`  
- Comando management: `python manage.py sync_architecture_prompts`  
- Cadastro inicial no PromptTemplate  
- Architecture Intelligence continua usando .md (sem mudança no service)

---

### Cenário D: Integração mínima — apenas documentação e tipo

**Ideia:** Adicionar tipo `avaliacao_arquitetural` em `PromptTemplate.TIPO_PROMPT_CHOICES` e documentar no `00_prompt_dos_prompts` que o Architecture Intelligence é um consumidor futuro. Sem alteração de código.

**Esforço estimado:** 0,5 dia  
- Migration para novo tipo  
- Atualização da documentação

---

## 3. Recomendação e esforço total

| Cenário | Esforço | Benefício |
|---------|---------|-----------|
| **A** | 2–3 dias | Architecture Intelligence usa prompts versionados no PostgreSQL |
| **B** | 3–4 dias | Service totalmente desacoplado de arquivos; prompts centralizados |
| **C** | 2 dias | Versionamento e Admin sem mudar o service |
| **D** | 0,5 dia | Apenas preparação para integração futura |

**Recomendação:** Começar pelo **Cenário C** (sync) e evoluir para **Cenário A** quando houver necessidade de trocar prompts em runtime sem redeploy.

**Esforço total para integração completa (A + C):** ~4–5 dias.

---

## 4. Pontos de integração no código

| Arquivo | Alteração |
|---------|-----------|
| `app_sinapum/models.py` | Adicionar `'avaliacao_arquitetural'` em TIPO_PROMPT_CHOICES |
| `app_architecture_intelligence/services.py` | Opcional: resolver prompt_ref e enviar no payload |
| `services/architecture_intelligence_service/app/api/schemas.py` | Adicionar `prompts_override: Optional[dict]` em StartCycleRequest |
| `services/architecture_intelligence_service/app/core/stages.py` | Se `prompts_override` presente, usar em vez de `_load_prompt()` |
| `app_mcp_tool_registry/utils.py` | Já suporta resolução; sem alteração |
| Novo: `app_architecture_intelligence/management/commands/sync_architecture_prompts.py` | Sync .md → PromptTemplate |

---

## 5. Dependências do Prompt dos Prompts

O `00_prompt_dos_prompts.md` define que novos prompts devem:

- Ter propósito claro
- Ser classificados em tipo (análise, curadoria, decisão)
- Declarar o que pode e não pode fazer
- Estar alinhados com Core_SinapUm, VitrineZap ou SKM

O Architecture Intelligence se encaixa como **análise** (avalia arquitetura, não decide). O tipo `avaliacao_arquitetural` pode ser um subtipo de análise ou um tipo próprio.
