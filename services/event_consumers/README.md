# Event Consumers

Consumidores de eventos do Event Bus (Redis Streams) para o ecossistema Core_SinapUm.

## Pré-requisitos

- Redis acessível (REDIS_URL)
- Python com redis: `pip install redis`
- Para core_consumer: Django (Core_SinapUm) configurado

## Variáveis de Ambiente

| Consumer | Variável | Descrição |
|----------|----------|-----------|
| core | REDIS_URL | URL do Redis |
| core | SINAPUM_WHATSAPP_WEBHOOK_URL | Webhook do Core para encaminhar eventos |
| evora | REDIS_URL | URL do Redis |
| evora | EVORA_WHATSAPP_WEBHOOK_URL | Webhook do Evora |
| shopperbot | REDIS_URL | URL do Redis |
| shopperbot | SHOPPERBOT_WHATSAPP_WEBHOOK_URL | Webhook do ShopperBot |

## Execução

```bash
# Do diretório Core_SinapUm
export REDIS_URL=redis://localhost:6379/0
export SINAPUM_WHATSAPP_WEBHOOK_URL=http://localhost:5000/webhooks/whatsapp/

# Core consumer (requer Django)
python services/event_consumers/core_consumer.py

# Evora consumer (standalone)
export EVORA_WHATSAPP_WEBHOOK_URL=https://evora-product.up.railway.app/webhooks/whatsapp/
python services/event_consumers/evora_consumer.py

# Ou usar o script
./scripts/run_event_consumers.sh core
./scripts/run_event_consumers.sh all
```

## Systemd (produção)

Exemplo de unit para core_consumer:

```ini
[Unit]
Description=Core Event Consumer
After=redis.service

[Service]
Type=simple
WorkingDirectory=/path/to/Core_SinapUm
Environment=REDIS_URL=redis://localhost:6379/0
Environment=DJANGO_SETTINGS_MODULE=setup.settings
ExecStart=/path/to/venv/bin/python services/event_consumers/core_consumer.py
Restart=always

[Install]
WantedBy=multi-user.target
```
