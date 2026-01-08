# WhatsApp Events - Eventos Canônicos v1.0

Sistema completo de eventos canônicos WhatsApp com roteamento, atribuição SKM e integração com SKM Score.

## 📋 Visão Geral

Este app implementa:
- **Eventos Canônicos**: Normalização de eventos de diferentes providers WhatsApp
- **Roteamento**: Thread determinístico e atribuição de SKM
- **Persistência**: EventLog, Conversation, ThreadParticipant, MessageIndex
- **SKM Score**: Catálogo de eventos que alimentam o sistema de score

## 🏗️ Estrutura

### Models

- **WhatsAppEventLog**: Log de todos os eventos canônicos
- **WhatsAppConversation**: Conversações/threads
- **WhatsAppThreadParticipant**: Participantes de conversações
- **WhatsAppMessageIndex**: Índice de mensagens para performance

### Utils

- `generate_idempotency_key()`: Gera chave de idempotência determinística
- `generate_thread_key()`: Gera chave de thread determinística
- `get_or_create_conversation()`: Obtém ou cria conversação
- `append_event()`: Adiciona evento ao log e atualiza conversação

## 🔗 Integração

### Com Core Services

```python
from core.services.whatsapp.canonical.schemas_v1 import EventEnvelope
from core.services.whatsapp_routing.router import get_whatsapp_router
from app_whatsapp_events.utils import append_event

# Rotear evento
router = get_whatsapp_router()
result = router.route_event(envelope)

# Ou persistir diretamente
event_log = append_event(envelope.to_dict())
```

### Com Normalizers

```python
from core.services.whatsapp.canonical.normalizer import get_event_normalizer
from app_whatsapp_events.utils import append_event

normalizer = get_event_normalizer()
envelope = normalizer.normalize(
    provider="evolution",
    raw_payload=webhook_payload
)

if envelope:
    event_log = append_event(envelope.to_dict())
```

## 📊 ERD

Ver `ERD.md` para diagrama completo de entidades e relacionamentos.

## 🚀 Uso

### Criar Evento Manualmente

```python
from core.services.whatsapp.canonical.schemas_v1 import (
    EventEnvelope, EventType, EventSource, Routing, Actor, Context, Message, Trace
)

envelope = EventEnvelope(
    event_type=EventType.MESSAGE_INBOUND,
    source=EventSource(provider="evolution", provider_message_id="msg_123"),
    routing=Routing(shopper_id="shopper_123", thread_key="whatsapp:5511999999999|shopper:shopper_123|group:null"),
    actor=Actor(role="customer", wa_id="5511999999999"),
    context=Context(chat_type="private"),
    message=Message(message_id="msg_123", direction="inbound", type="text", text="Olá!"),
    trace=Trace(idempotency_key="hash_123"),
)

from app_whatsapp_events.utils import append_event
event_log = append_event(envelope.to_dict())
```

### Buscar Eventos

```python
from app_whatsapp_events.models import WhatsAppEventLog, WhatsAppConversation

# Por thread
events = WhatsAppEventLog.objects.filter(thread_key=thread_key).order_by('-occurred_at')

# Por conversação
conversation = WhatsAppConversation.objects.get(thread_key=thread_key)
events = WhatsAppEventLog.objects.filter(conversation_id=conversation.conversation_id)

# Por SKM
events = WhatsAppEventLog.objects.filter(skm_id=skm_id).order_by('-occurred_at')
```

## ⚙️ Configuração

### Feature Flags

```bash
# Habilitar eventos canônicos
WHATSAPP_CANONICAL_EVENTS_ENABLED=true

# Modo shadow (não persiste)
WHATSAPP_CANONICAL_SHADOW_MODE=true

# Habilitar roteamento
WHATSAPP_ROUTING_ENABLED=true

# Habilitar roteamento em grupo
WHATSAPP_GROUP_ROUTING_ENABLED=true

# Política de atribuição
WHATSAPP_ASSIGNMENT_POLICY=default  # default|round_robin|sticky
```

## 📚 Documentação

- **ERD.md**: Diagrama de entidades e relacionamentos
- **EVENT_CATALOG.md**: Catálogo completo de event_types
- **ROLLOUT_CHECKLIST.md**: Checklist de rollout seguro

## 🔄 Migrations

```bash
python manage.py makemigrations app_whatsapp_events
python manage.py migrate app_whatsapp_events
```

## ✅ Garantias

- ✅ **Idempotência**: Eventos duplicados são ignorados
- ✅ **Thread Determinístico**: Thread_key sempre igual para mesma conversa
- ✅ **Auditoria**: Todos os eventos são persistidos
- ✅ **Performance**: Índices otimizados para consultas rápidas
- ✅ **Extensível**: Fácil adicionar novos event_types
