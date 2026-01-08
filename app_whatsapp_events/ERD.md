# ERD - WhatsApp Events Database

Modelagem de dados para eventos canônicos WhatsApp e roteamento.

## 📊 Diagrama de Entidades

```
┌─────────────────────────────────────┐
│      WhatsAppEventLog               │
├─────────────────────────────────────┤
│ PK  id (UUID)                        │
│     event_id (unique)                │
│     event_type                       │
│     occurred_at                      │
│     provider                         │
│     provider_message_id              │
│     idempotency_key (unique)         │
│     correlation_id                   │
│     shopper_id                       │
│     skm_id                           │
│     conversation_id (FK)             │
│     thread_key                       │
│     actor_wa_id                      │
│     chat_type                        │
│     message_type                     │
│     payload_json (JSON)              │
│     raw_provider_payload (JSON)      │
│     risk_flags (JSON)                │
│     created_at                       │
└─────────────────────────────────────┘
              │
              │ FK
              ▼
┌─────────────────────────────────────┐
│    WhatsAppConversation             │
├─────────────────────────────────────┤
│ PK  id (UUID)                        │
│     conversation_id (unique)         │
│     thread_key (unique)              │
│     shopper_id                       │
│     skm_id                           │
│     keeper_id                        │
│     status                           │
│     last_event_at                    │
│     last_actor_wa_id                 │
│     tags (JSON)                      │
│     created_at                       │
│     updated_at                       │
└─────────────────────────────────────┘
              │
              │ 1:N
              ▼
┌─────────────────────────────────────┐
│  WhatsAppThreadParticipant          │
├─────────────────────────────────────┤
│ PK  id (UUID)                        │
│ FK  conversation_id                 │
│     wa_id                           │
│     role                            │
│     display_name                    │
│     first_seen_at                   │
│     last_seen_at                    │
│     is_blocked                      │
│ UNIQUE (conversation_id, wa_id)    │
└─────────────────────────────────────┘

┌─────────────────────────────────────┐
│    WhatsAppMessageIndex             │
├─────────────────────────────────────┤
│ PK  id (UUID)                        │
│     provider_message_id (unique)     │
│     message_id (UUID)                │
│ FK  conversation_id                 │
│     direction                        │
│     message_type                     │
│     occurred_at                      │
└─────────────────────────────────────┘
              │
              │ FK
              ▼
    (WhatsAppConversation)
```

## 🔗 Relacionamentos

### WhatsAppEventLog → WhatsAppConversation
- **Tipo**: Many-to-One (N:1)
- **FK**: `conversation_id` → `conversation_id`
- **Descrição**: Múltiplos eventos pertencem a uma conversação

### WhatsAppConversation → WhatsAppThreadParticipant
- **Tipo**: One-to-Many (1:N)
- **FK**: `conversation_id` → `conversation_id`
- **Descrição**: Uma conversação tem múltiplos participantes

### WhatsAppMessageIndex → WhatsAppConversation
- **Tipo**: Many-to-One (N:1)
- **FK**: `conversation_id` → `conversation_id`
- **Descrição**: Múltiplos índices de mensagem pertencem a uma conversação

## 📋 Índices

### WhatsAppEventLog
- `idempotency_key` (unique) - Idempotência
- `thread_key` - Busca por thread
- `provider_message_id` - Busca por mensagem do provider
- `occurred_at` - Ordenação temporal
- `event_type, occurred_at` - Busca por tipo
- `conversation_id, occurred_at` - Eventos por conversação
- `shopper_id, occurred_at` - Eventos por shopper
- `skm_id, occurred_at` - Eventos por SKM

### WhatsAppConversation
- `thread_key` (unique) - Busca por thread
- `last_event_at` - Ordenação por atividade
- `status, last_event_at` - Conversações por status
- `shopper_id, last_event_at` - Conversações por shopper
- `skm_id, last_event_at` - Conversações por SKM

### WhatsAppThreadParticipant
- `conversation_id, wa_id` (unique) - Participante único por conversação
- `role, last_seen_at` - Participantes por role

### WhatsAppMessageIndex
- `provider_message_id` (unique) - Busca por mensagem do provider
- `conversation_id, occurred_at` - Mensagens por conversação
- `direction, occurred_at` - Mensagens por direção

## 🔑 Chaves e Constraints

### Primary Keys
- Todos os modelos usam `UUID` como PK

### Unique Constraints
- `WhatsAppEventLog.idempotency_key` - Garante idempotência
- `WhatsAppConversation.conversation_id` - ID único da conversação
- `WhatsAppConversation.thread_key` - Thread único
- `WhatsAppThreadParticipant(conversation_id, wa_id)` - Participante único
- `WhatsAppMessageIndex.provider_message_id` - Mensagem única do provider

## 📊 Campos JSON

### WhatsAppEventLog.payload_json
Armazena payload específico do evento:
```json
{
  "text": "...",
  "media": {...},
  "interactive": {...}
}
```

### WhatsAppEventLog.raw_provider_payload
Armazena payload bruto do provider:
```json
{
  "provider": "evolution",
  "provider_payload": {...}
}
```

### WhatsAppEventLog.risk_flags
Armazena flags de risco:
```json
["multiple_failures", "chargeback_risk"]
```

### WhatsAppConversation.tags
Armazena tags da conversação:
```json
["vip", "urgent", "refund"]
```

## 🔄 Fluxo de Dados

1. **Evento Recebido** → `append_event()` cria `WhatsAppEventLog`
2. **Thread Resolvido** → `get_or_create_conversation()` cria/atualiza `WhatsAppConversation`
3. **Participante Atualizado** → Cria/atualiza `WhatsAppThreadParticipant`
4. **Índice Criado** → Cria `WhatsAppMessageIndex` (se aplicável)

## 🎯 Casos de Uso

### Buscar Eventos por Thread
```python
events = WhatsAppEventLog.objects.filter(thread_key=thread_key).order_by('-occurred_at')
```

### Buscar Conversação por Thread
```python
conversation = WhatsAppConversation.objects.get(thread_key=thread_key)
```

### Buscar Participantes de uma Conversação
```python
participants = conversation.participants.all()
```

### Buscar Mensagens por Conversação
```python
messages = conversation.message_indexes.filter(direction='inbound').order_by('-occurred_at')
```

### Verificar Idempotência
```python
exists = WhatsAppEventLog.objects.filter(idempotency_key=key).exists()
```
