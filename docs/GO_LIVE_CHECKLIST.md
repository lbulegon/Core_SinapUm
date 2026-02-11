# Checklist — Go-live controlado (Core_SinapUm)

Use este checklist antes e no primeiro dia de produção. Não pule itens.

---

## Antes de subir em produção

- [ ] **WHATSAPP_GATEWAY_URL** correto (container ↔ host ↔ rede)
- [ ] **DATABASE_URL** ou **POSTGRES_*** iguais aos do web
- [ ] **CELERY_BROKER_URL** apontando para o Redis certo
- [ ] Worker com **--concurrency** baixo (1–2) inicialmente
- [ ] **SEMANTIC_CACHE_ENABLED=false** até embeddings estarem validados

---

## Primeiro teste real

1. Subir worker:
   ```bash
   docker compose -f docker-compose.worker.yml up -d
   ```

2. Enviar evento fake (no container web: `docker compose exec web python manage.py shell`):
   ```python
   from core.services.task_queue_service.tasks import ingest_event
   ingest_event.delay("evt_smoke_001", "whatsapp", {
       "text": "oi",
       "user_id": "5511999999999",
       "channel": "whatsapp"
   })
   ```

3. Ver logs:
   ```bash
   docker logs -f core_celery_worker
   ```

---

## Ativar cache depois

1. Instalar sentence-transformers (já no `requirements-worker.txt`).
2. Setar:
   ```bash
   SEMANTIC_CACHE_ENABLED=true
   ```
3. Conferir criação do índice RedisVL nos logs do worker.

---

## Leitura estratégica

Hoje vocês têm:

**Uma espinha dorsal conversacional orientada a eventos**, com execução assíncrona, idempotência, observabilidade e porta aberta para inteligência real (MCP + cache semântico).

Isso não é um bot.
