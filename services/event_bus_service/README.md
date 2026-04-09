# Event Bus Service

Serviço de barramento de eventos baseado em **Redis Streams** para o ecossistema Core_SinapUm.

## Arquitetura

```
WhatsApp → whatsapp_gateway_service → Event Bus (Redis Streams)
                                            │
                    ┌───────────────────────┼───────────────────────┐
                    ▼                       ▼                       ▼
            Core Consumer           Evora Consumer          ShopperBot Consumer
```

## Streams (Tópicos)

| Stream | Descrição | Consumidores |
|--------|-----------|---------------|
| `whatsapp.inbound` | Mensagens recebidas, QR, connected, disconnected | Core, Evora |
| `whatsapp.outbound` | Mensagens enviadas (auditoria) | - |
| `leads.captured` | Leads capturados | Core |
| `orders.created` | Pedidos criados | ShopperBot |

## Formato de Evento

```json
{
  "event": "whatsapp.message.received",
  "instance_id": "default",
  "jid": "5511999999999@s.whatsapp.net",
  "payload": {
    "key": { "remoteJid": "...", "id": "..." },
    "message": { "conversation": "..." },
    "messageTimestamp": 1234567890
  },
  "timestamp": "2026-03-11T12:00:00.000Z",
  "source": "whatsapp_gateway_service"
}
```

## Variáveis de Ambiente

| Variável | Descrição | Padrão |
|----------|-----------|--------|
| `REDIS_URL` | URL do Redis | `redis://localhost:6379/0` |
| `EVENT_BUS_ENABLED` | Habilitar publicação | `true` |
| `WEBHOOK_URL` | Webhook legado (opcional) | - |

## Uso

```bash
# Publicar evento (via API ou gateway)
curl -X POST http://localhost:8008/events \
  -H "Content-Type: application/json" \
  -d '{"event":"whatsapp.message.received","instance_id":"default","payload":{}}'

# Consumir (Python)
python -m event_bus_service.consumers.core_consumer
```
