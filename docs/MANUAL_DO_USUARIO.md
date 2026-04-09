# Manual do Usuário — Core_SinapUm

Este manual descreve o uso e a operação do **Core_SinapUm** como orquestrador de eventos conversacionais.

---

## 1. O que é o Core_SinapUm

O Core_SinapUm é a espinha dorsal do fluxo conversacional:

- Recebe eventos (ex.: mensagens WhatsApp) e grava no banco.
- Processa em background com Celery (filas e workers).
- Consulta o Evora (MCP) para decisão de rota e registro de mensagens.
- Opcionalmente usa cache semântico (RedisVL).
- Envia mensagens para o usuário via WhatsApp Gateway (HTTP).

O Core orquestra e executa; o Evora decide e audita.

---

## 2. Componentes principais

| Componente | Função |
|------------|--------|
| Web (Django) | API, admin, ingestão de eventos. |
| Worker (Celery) | Consome filas, processa eventos, chama MCP, cache e WhatsApp. |
| Redis | Broker Celery + resultados + idempotência + (opcional) RedisVL. |
| PostgreSQL | Banco do Django; worker usa o mesmo banco que o web. |

---

## 3. Configuração

- **Banco:** DATABASE_URL ou POSTGRES_* (mesmos do web).
- **Celery:** CELERY_BROKER_URL, CELERY_RESULT_BACKEND (Redis).
- **WhatsApp:** WHATSAPP_GATEWAY_URL (obrigatório para envio real), SINAPUM_WHATSAPP_GATEWAY_API_KEY (opcional).
- **Evora MCP:** EVORA_MCP_URL; opcional EVORA_MCP_TOKEN. Sem URL = fallback (stub).
- **Cache semântico:** SEMANTIC_CACHE_ENABLED, SEMANTIC_EMBEDDINGS_PROVIDER, etc.

Ver: docs/ENV_CORE_SINAPUM_EXEMPLO.md e docs/GO_LIVE_CHECKLIST.md.

---

## 4. Operação

### Subir o worker

```bash
cd /root/Core_SinapUm
docker compose -f docker-compose.worker.yml up -d --build
```

### Logs do worker

```bash
docker logs -f core_celery_worker
```

### Teste rápido (shell no web)

```bash
docker compose exec web python manage.py shell
```

No shell Python:

```python
from core.services.task_queue_service.tasks import ingest_event
ingest_event.delay("evt_smoke_001", "whatsapp", {"text": "oi", "user_id": "5511999999999", "channel": "whatsapp"})
```

Acompanhe os logs do worker.

---

## 5. Fluxo de um evento

1. Ingestão: ingest_event.delay() grava InboundEvent e enfileira process_inbound_event.
2. Worker processa, lock Redis por event_id (idempotência).
3. Evora MCP: policy.decide (rota, allow_ai) e domain.append_message (auditoria).
4. Cache semântico (opcional): consulta RedisVL.
5. Resposta: LLM ou template; envio via WhatsApp Gateway.
6. Evento marcado PROCESSED/FAILED.

---

## 6. Documentos de referência

- Checklist produção: docs/GO_LIVE_CHECKLIST.md
- Variáveis de ambiente: docs/ENV_CORE_SINAPUM_EXEMPLO.md
- Worker e filas: docs/WORKER_CELERY.md
- MCP Evora HTTP: docs/PATCH_EVORA_CALL_TOOL_HTTP.md
