# WhatsApp Canonical Events v1.0

Sistema de eventos canônicos para padronizar eventos de diferentes providers WhatsApp.

## 📋 Características

- ✅ **100% Aditivo**: Não altera código existente
- ✅ **Feature Flags**: Controlado por variáveis de ambiente
- ✅ **Modo Shadow**: Gera eventos sem persistir (para testes)
- ✅ **Idempotência**: Evita processamento duplicado
- ✅ **Multi-Provider**: Suporta Evolution, Cloud API, Baileys, Simulated
- ✅ **Signals**: Emite signals para pipeline conversacional
- ✅ **Auditoria**: Persiste todos os eventos em EventLog

## 🚀 Uso Básico

### Receber Evento Canônico

```python
from core.services.whatsapp.canonical.schemas import EventEnvelope, EventType
from core.services.whatsapp.canonical.publisher import get_event_publisher

# Criar envelope
envelope = EventEnvelope(
    event_type=EventType.MESSAGE_TEXT,
    event_source=EventSource.EVOLUTION,
    instance_key="instance_123",
    from_number="5511999999999",
    payload=MessagePayload(text="Olá!"),
    raw={"provider": "evolution", "provider_payload": {...}}
)

# Publicar
publisher = get_event_publisher()
event_log = publisher.publish(envelope)
```

### Normalizar Evento de Provider

```python
from core.services.whatsapp.canonical.normalizer import get_event_normalizer

normalizer = get_event_normalizer()
envelope = normalizer.normalize(
    provider="evolution",
    raw_payload=webhook_payload,
    instance_key="instance_123"
)
```

### Usar Compat Layer

```python
from core.services.whatsapp.canonical.compat import get_webhook_compat_layer

# Wrapper para webhook existente
compat = get_webhook_compat_layer()
wrapped_handler = compat.wrap_webhook_handler(
    original_handler=my_webhook_handler,
    provider="evolution",
    instance_key="instance_123"
)
```

## ⚙️ Configuração

### Variáveis de Ambiente

```bash
# Habilitar eventos canônicos
WHATSAPP_CANONICAL_EVENTS_ENABLED=true

# Modo shadow (gera eventos sem persistir)
WHATSAPP_CANONICAL_SHADOW_MODE=false
```

### Settings.py

```python
WHATSAPP_CANONICAL_EVENTS_ENABLED = True
WHATSAPP_CANONICAL_SHADOW_MODE = False
```

## 📊 Tipos de Eventos

### Mensagens

- `message.text` - Mensagem de texto
- `message.media` - Mensagem de mídia (imagem, vídeo, áudio, documento)
- `message.location` - Mensagem de localização
- `message.contact` - Mensagem de contato
- `message.button` - Mensagem com botão
- `message.list` - Mensagem de lista

### Status

- `message.sent` - Mensagem enviada
- `message.delivered` - Mensagem entregue
- `message.read` - Mensagem lida
- `message.failed` - Mensagem falhou

### Instância

- `instance.connected` - Instância conectada
- `instance.disconnected` - Instância desconectada
- `instance.qr_updated` - QR code atualizado
- `instance.connection_update` - Atualização de conexão

## 🔌 Endpoints

### POST /api/v1/whatsapp/events/inbound

Recebe evento canônico de entrada (mensagem recebida).

**Payload:**
```json
{
  "event_id": "uuid",
  "event_type": "message.text",
  "event_source": "evolution",
  "instance_key": "instance_123",
  "timestamp": "2024-01-01T12:00:00Z",
  "from_number": "5511999999999",
  "payload": {
    "text": "Mensagem de teste"
  },
  "raw": {
    "provider": "evolution",
    "provider_payload": {...}
  }
}
```

### POST /api/v1/whatsapp/events/status

Recebe evento canônico de status.

**Payload:**
```json
{
  "event_id": "uuid",
  "event_type": "message.delivered",
  "event_source": "evolution",
  "instance_key": "instance_123",
  "timestamp": "2024-01-01T12:00:00Z",
  "message_id": "msg_123",
  "payload": {
    "status": "delivered",
    "message_id": "msg_123"
  }
}
```

### GET /api/v1/whatsapp/events/health

Health check do sistema de eventos canônicos.

## 🔄 Idempotência

O sistema garante idempotência usando `provider_event_id` e `provider_message_id`.

- Se um evento com o mesmo `provider_event_id` já foi processado, não será processado novamente
- Evita duplicação de eventos em caso de retry de webhooks

## 📝 Exemplos de Payload

### Evolution API - Mensagem de Texto

```json
{
  "event": "messages.upsert",
  "data": {
    "key": {
      "remoteJid": "5511999999999@s.whatsapp.net",
      "id": "msg_123"
    },
    "message": {
      "conversation": "Olá!"
    },
    "messageTimestamp": 1704110400
  }
}
```

**Normalizado para:**
```json
{
  "event_type": "message.text",
  "event_source": "evolution",
  "from_number": "5511999999999",
  "message_id": "msg_123",
  "payload": {
    "text": "Olá!"
  }
}
```

### Cloud API - Mensagem de Texto

```json
{
  "entry": [{
    "changes": [{
      "value": {
        "messages": [{
          "from": "5511999999999",
          "id": "msg_123",
          "type": "text",
          "text": {
            "body": "Olá!"
          },
          "timestamp": "1704110400"
        }]
      }
    }]
  }]
}
```

**Normalizado para:**
```json
{
  "event_type": "message.text",
  "event_source": "cloud",
  "from_number": "5511999999999",
  "message_id": "msg_123",
  "payload": {
    "text": "Olá!"
  }
}
```

## 🔧 Integração com Webhooks Existentes

### Usando Compat Layer

```python
from core.services.whatsapp.canonical.compat import get_webhook_compat_layer

# Webhook handler original
def my_webhook_handler(request):
    # Lógica existente
    return Response({"success": True})

# Wrapper com compat layer
compat = get_webhook_compat_layer()
wrapped_handler = compat.wrap_webhook_handler(
    original_handler=my_webhook_handler,
    provider="evolution",
    instance_key="instance_123"
)

# Usar wrapped_handler no lugar do original
```

### Processar Payload Manualmente

```python
from core.services.whatsapp.canonical.compat import get_webhook_compat_layer

compat = get_webhook_compat_layer()
envelope = compat.process_webhook_payload(
    provider="evolution",
    raw_payload=request.data,
    instance_key="instance_123",
    persist=True  # False para shadow mode
)
```

## 📊 Signals

O sistema emite signals quando eventos são publicados:

```python
from django.dispatch import receiver
from core.services.whatsapp.canonical.publisher import canonical_event_received
from core.services.whatsapp.canonical.schemas import EventEnvelope

@receiver(canonical_event_received)
def handle_canonical_event(sender, envelope: EventEnvelope, event_log, **kwargs):
    """Processar evento canônico"""
    if envelope.is_message_event():
        # Processar mensagem
        pass
```

## 🧪 Testar sem Persistir

### Modo Shadow

```bash
WHATSAPP_CANONICAL_EVENTS_ENABLED=true
WHATSAPP_CANONICAL_SHADOW_MODE=true
```

Em shadow mode:
- Eventos são normalizados
- Eventos são logados
- Eventos NÃO são persistidos no EventLog
- Signals NÃO são emitidos

## 📚 Tabela de Event Types

| Event Type | Descrição | Payload |
|------------|-----------|---------|
| `message.text` | Mensagem de texto | `MessagePayload` |
| `message.media` | Mensagem de mídia | `MediaPayload` |
| `message.location` | Mensagem de localização | `LocationPayload` |
| `message.contact` | Mensagem de contato | `ContactPayload` |
| `message.button` | Mensagem com botão | `ButtonPayload` |
| `message.list` | Mensagem de lista | `ListPayload` |
| `message.sent` | Mensagem enviada | `StatusPayload` |
| `message.delivered` | Mensagem entregue | `StatusPayload` |
| `message.read` | Mensagem lida | `StatusPayload` |
| `message.failed` | Mensagem falhou | `StatusPayload` |
| `instance.connected` | Instância conectada | `dict` |
| `instance.disconnected` | Instância desconectada | `dict` |
| `instance.qr_updated` | QR code atualizado | `dict` |
| `instance.connection_update` | Atualização de conexão | `dict` |

## 🔄 Migração Gradual

### Fase 0: Shadow Mode (Default)

```bash
WHATSAPP_CANONICAL_EVENTS_ENABLED=true
WHATSAPP_CANONICAL_SHADOW_MODE=true
```

- Eventos são normalizados e logados
- Eventos NÃO são persistidos
- Webhooks existentes continuam funcionando

### Fase 1: Persistência Ativada

```bash
WHATSAPP_CANONICAL_EVENTS_ENABLED=true
WHATSAPP_CANONICAL_SHADOW_MODE=false
```

- Eventos são normalizados e persistidos
- Signals são emitidos
- Webhooks existentes continuam funcionando

### Fase 2: Endpoints Canônicos

Migrar webhooks para usar endpoints canônicos:

```bash
# Antes: /webhooks/evolution/...
# Depois: /api/v1/whatsapp/events/inbound
```

## ⚠️ Garantias

- ✅ **Não Quebra**: Webhooks existentes continuam funcionando
- ✅ **Idempotência**: Eventos duplicados são ignorados
- ✅ **Auditoria**: Todos os eventos são logados
- ✅ **Feature Flags**: Pode ser desabilitado a qualquer momento
- ✅ **Shadow Mode**: Pode testar sem persistir

## 📊 Modelo de Dados

### CanonicalEventLog

- `event_id` - ID único do evento
- `event_type` - Tipo do evento
- `event_source` - Fonte (provider)
- `instance_key` - Chave da instância
- `from_number` - Número de origem
- `to_number` - Número de destino
- `payload` - Payload específico (JSON)
- `raw_payload` - Payload bruto do provider (JSON)
- `message_id` - ID da mensagem
- `correlation_id` - ID de correlação
- `shopper_id` - ID do shopper
- `skm_id` - SKM ID
- `provider_event_id` - ID do evento no provider (idempotência)
- `provider_message_id` - ID da mensagem no provider
- `timestamp` - Timestamp do evento
- `created_at` - Timestamp de criação
- `processed_at` - Timestamp de processamento
