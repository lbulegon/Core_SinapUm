# PROMPT 1 — CORE_SINAPUM (VERSÃO CORRIGIDA)

Arquivo: `/root/Core_SinapUm/00_prompt_celery_redisvl_mcp.md`

---

## CONTEXTO CRÍTICO (LEIA COM ATENÇÃO)

Existe um projeto **JÁ CRIADO** e **EM USO** localizado em:

**`/root/Core_SinapUm`**

- **NÃO** crie um novo projeto.
- **NÃO** altere o nome da pasta.
- **NÃO** duplique estrutura.
- **NÃO** crie `/root/core_sinapum`.

Todo o trabalho deve:
- analisar a estrutura **EXISTENTE** em `/root/Core_SinapUm`
- respeitar padrões já adotados
- adicionar novos serviços de forma **incremental**
- manter compatibilidade com o código atual

---

## Papel

Você é um engenheiro sênior responsável por **EVOLUIR** o projeto existente Core_SinapUm como orquestrador central de eventos, tarefas assíncronas, cache semântico e governança de IA.

---

## OBJETIVO

Estender o Core_SinapUm para que ele:

- receba eventos externos (ex: WhatsApp Gateway)
- registre eventos brutos para auditoria e deduplicação
- processe eventos de forma assíncrona com Celery
- utilize RedisVL como cache semântico central
- utilize MCP como contrato vivo para comunicação com serviços de domínio (Evora)
- centralize chamadas de IA com versionamento, custos e observabilidade

---

## RESTRIÇÕES ARQUITETURAIS

- O Core_SinapUm **NÃO** contém regras de negócio do VitrineZap
- O Core_SinapUm **NÃO** decide lógica de domínio
- O Core_SinapUm apenas orquestra, executa, cacheia e observa
- Toda comunicação com Evora deve ocorrer **via MCP**
- Toda persistência deve usar **JSON estruturado** (event sourcing leve)
- **NÃO** remover código existente sem justificativa explícita

---

## STACK (MANTER)

- Python
- Framework atual do Core (Django/FastAPI — detectar automaticamente)
- Redis (já existente ou a ser configurado)
- Celery
- RedisVL
- MCP
- Pydantic

---

## IMPLEMENTAÇÕES OBRIGATÓRIAS

### 1) TASK QUEUE SERVICE (INCREMENTAL)

Criar (ou integrar) em `/root/Core_SinapUm/services/task_queue_service/` ou em `core/services/task_queue_service/`:

- `celery_app.py` (configurar Celery usando Redis)
- Filas: `events_ingest`, `domain_processing`, `ai_calls`, `metrics_batch`, `webhooks_out`
- Suporte a retry, backoff e idempotência por `event_id`

### 2) EVENT INGESTION

Modelo persistente `InboundEvent` (ou equivalente):

- `event_id`, `source`, `payload_json`, `received_at`, `processed_at`, `status`
- Task: `process_inbound_event(event_id)`

### 3) MCP CLIENT (EVORA)

- `evora.policy.decide`
- `evora.domain.append_message`
- `contract_version`, `policy_version`, timeout e retry controlados

### 4) SEMANTIC CACHE SERVICE

- Índice RedisVL (embedding + metadata)
- `query(intent, context)`, `store(intent, context, response)`
- Métricas: hit_rate, latency, estimated_token_savings

### 5) IA COMO SERVIÇO (GOVERNADO)

- IA só via Celery; registrar prompt_version, modelo, custo, latência; nenhuma chamada direta via HTTP

### 6) FLUXO OBRIGATÓRIO

- evento → persistir InboundEvent → enfileirar process_inbound_event → evora.policy.decide → cache semântico → se miss e permitido → IA → gateway → notificar Evora

### 7) OBSERVABILIDADE

- Por evento: fila, tempo total, cache hit/miss, custo IA, contract_version, prompt_version

---

## RESULTADO ESPERADO

- Core_SinapUm **evoluído**, não recriado
- Arquitetura consistente com Celery + RedisVL
- MCP como contrato vivo
- IA governada, cacheada e auditável
- Infra preparada para múltiplos canais futuros
