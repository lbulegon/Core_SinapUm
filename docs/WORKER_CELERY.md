# Worker Celery — Core_SinapUm

## Build e run

```bash
cd /root/Core_SinapUm
docker compose -f docker-compose.worker.yml up -d --build
```

## Logs

```bash
docker logs -f core_celery_worker
```

## Comando Celery (filas)

O worker sobe com:

- Filas: `events_ingest`, `domain_processing`, `ai_calls`, `metrics_batch`, `webhooks_out`
- Concorrência: 2

Para rodar manualmente com as mesmas filas:

```bash
celery -A setup worker -l INFO -Q events_ingest,domain_processing,ai_calls,metrics_batch,webhooks_out --concurrency=2
```

## Teste rápido (shell no web)

```bash
docker compose exec web python manage.py shell
```

No shell:

```python
from core.services.task_queue_service.tasks import ingest_event
ingest_event.delay("evt_test_001", "test", {"text": "oi", "user_id": "u1", "channel": "whatsapp"})
```

Acompanhe no log do worker.

## Dois workers (rápido vs pesado)

- **Worker A (rápido):** `events_ingest`, `domain_processing`, `webhooks_out`
- **Worker B (pesado):** `ai_calls`, `metrics_batch`

Exemplo worker pesado:

```bash
celery -A setup worker -l INFO -Q ai_calls,metrics_batch --concurrency=1
```

No compose você pode duplicar o service `worker` com outro nome e outro `command`.
