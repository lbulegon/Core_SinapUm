# Catálogo de Eventos Canônicos WhatsApp v1.0

Catálogo completo de event_types que alimentam o SKM Score e sistema de governança.

## 📋 WhatsApp Events

| Event Type | Descrição | Impacto SKM | Severidade | Campos Mínimos |
|------------|-----------|-------------|------------|----------------|
| `whatsapp.message.inbound` | Mensagem recebida | Neutro | Low | `actor.wa_id`, `message.text`, `routing.shopper_id` |
| `whatsapp.message.outbound` | Mensagem enviada | Neutro | Low | `actor.wa_id`, `message.text`, `routing.skm_id` |
| `whatsapp.message.status.queued` | Mensagem na fila | Neutro | Low | `message.message_id`, `routing.skm_id` |
| `whatsapp.message.status.sent` | Mensagem enviada | Positivo | Low | `message.message_id`, `routing.skm_id` |
| `whatsapp.message.status.delivered` | Mensagem entregue | Positivo | Med | `message.message_id`, `routing.skm_id` |
| `whatsapp.message.status.read` | Mensagem lida | Positivo | Med | `message.message_id`, `routing.skm_id` |
| `whatsapp.message.status.failed` | Mensagem falhou | Negativo | High | `message.message_id`, `routing.skm_id`, `security.risk_flags` |
| `whatsapp.thread.assigned` | Thread atribuído a SKM | Neutro | Low | `routing.thread_key`, `routing.skm_id`, `routing.shopper_id` |
| `whatsapp.conversation.opened` | Conversação aberta | Neutro | Low | `routing.conversation_id`, `routing.thread_key` |
| `whatsapp.conversation.closed` | Conversação fechada | Neutro | Low | `routing.conversation_id`, `routing.thread_key` |
| `whatsapp.group.joined` | Entrou em grupo | Neutro | Low | `context.group.id`, `actor.wa_id` |
| `whatsapp.group.left` | Saiu do grupo | Neutro | Low | `context.group.id`, `actor.wa_id` |

## 💰 Commerce Events

| Event Type | Descrição | Impacto SKM | Severidade | Campos Mínimos |
|------------|-----------|-------------|------------|----------------|
| `commerce.intent.detected` | Intenção de compra detectada | Positivo | Med | `commerce.intent`, `routing.shopper_id`, `routing.skm_id` |
| `commerce.cart.created` | Carrinho criado | Positivo | Med | `commerce.product_ref`, `routing.shopper_id`, `routing.skm_id` |
| `commerce.order.created` | Pedido criado | Positivo | High | `commerce.order_ref`, `commerce.price_context`, `routing.shopper_id`, `routing.skm_id` |
| `commerce.payment.pending` | Pagamento pendente | Neutro | Med | `commerce.order_ref`, `routing.shopper_id`, `routing.skm_id` |
| `commerce.payment.confirmed` | Pagamento confirmado | Positivo | High | `commerce.order_ref`, `commerce.price_context`, `routing.shopper_id`, `routing.skm_id` |
| `commerce.refund.requested` | Reembolso solicitado | Negativo | High | `commerce.order_ref`, `routing.shopper_id`, `routing.skm_id` |
| `commerce.refund.completed` | Reembolso completado | Negativo | High | `commerce.order_ref`, `routing.shopper_id`, `routing.skm_id` |
| `commerce.chargeback.opened` | Chargeback aberto | Negativo | High | `commerce.order_ref`, `routing.shopper_id`, `routing.skm_id`, `security.risk_flags` |
| `commerce.chargeback.won` | Chargeback ganho | Positivo | High | `commerce.order_ref`, `routing.shopper_id`, `routing.skm_id` |
| `commerce.chargeback.lost` | Chargeback perdido | Negativo | High | `commerce.order_ref`, `routing.shopper_id`, `routing.skm_id`, `security.risk_flags` |

## 🚚 Delivery Events (AEP)

| Event Type | Descrição | Impacto SKM | Severidade | Campos Mínimos |
|------------|-----------|-------------|------------|----------------|
| `delivery.area.created` | Área de entrega criada | Neutro | Low | `routing.shopper_id`, `routing.skm_id`, `commerce.order_ref` |
| `delivery.link.sent` | Link de entrega enviado | Positivo | Low | `routing.shopper_id`, `routing.skm_id`, `commerce.order_ref` |
| `delivery.area.opened` | Área de entrega aberta | Positivo | Med | `routing.shopper_id`, `commerce.order_ref` |
| `delivery.content.viewed` | Conteúdo visualizado | Positivo | Low | `routing.shopper_id`, `commerce.order_ref` |
| `delivery.content.downloaded` | Conteúdo baixado | Positivo | Med | `routing.shopper_id`, `commerce.order_ref` |
| `delivery.confirmation.received` | Confirmação de entrega recebida | Positivo | High | `routing.shopper_id`, `routing.skm_id`, `commerce.order_ref` |
| `delivery.access.revoked` | Acesso revogado | Negativo | Med | `routing.shopper_id`, `commerce.order_ref`, `security.risk_flags` |

## 🚨 Regras Anti-Fraude

Eventos que disparam `security.risk_flags`:

1. **Múltiplas falhas de mensagem** (`whatsapp.message.status.failed`)
   - Flag: `multiple_failures`
   - Dispara após 3 falhas consecutivas

2. **Chargeback aberto** (`commerce.chargeback.opened`)
   - Flag: `chargeback_risk`
   - Dispara imediatamente

3. **Reembolso frequente** (`commerce.refund.requested`)
   - Flag: `refund_pattern`
   - Dispara após 2 reembolsos em 30 dias

4. **Acesso revogado** (`delivery.access.revoked`)
   - Flag: `access_revoked`
   - Dispara imediatamente

5. **Assinatura inválida** (`security.signature_valid = false`)
   - Flag: `invalid_signature`
   - Dispara imediatamente

## 📊 Impacto no SKM Score

### Eventos Positivos (aumentam score)
- `whatsapp.message.status.sent` (+1)
- `whatsapp.message.status.delivered` (+2)
- `whatsapp.message.status.read` (+3)
- `commerce.intent.detected` (+5)
- `commerce.cart.created` (+5)
- `commerce.order.created` (+10)
- `commerce.payment.confirmed` (+15)
- `commerce.chargeback.won` (+20)
- `delivery.area.opened` (+2)
- `delivery.content.downloaded` (+3)
- `delivery.confirmation.received` (+10)

### Eventos Negativos (diminuem score)
- `whatsapp.message.status.failed` (-5)
- `commerce.refund.requested` (-10)
- `commerce.refund.completed` (-15)
- `commerce.chargeback.opened` (-20)
- `commerce.chargeback.lost` (-30)
- `delivery.access.revoked` (-5)

### Eventos Neutros (não alteram score)
- `whatsapp.message.inbound`
- `whatsapp.message.outbound`
- `whatsapp.thread.assigned`
- `whatsapp.conversation.opened`
- `whatsapp.conversation.closed`
- `whatsapp.group.joined`
- `whatsapp.group.left`
- `commerce.payment.pending`
- `delivery.area.created`
- `delivery.link.sent`
- `delivery.content.viewed`

## 🔍 Campos Mínimos por Categoria

### WhatsApp Events
- `actor.wa_id` (obrigatório)
- `routing.shopper_id` (obrigatório para roteamento)
- `routing.skm_id` (obrigatório para atribuição)
- `message.message_id` (obrigatório para status)

### Commerce Events
- `commerce.order_ref` (obrigatório)
- `routing.shopper_id` (obrigatório)
- `routing.skm_id` (obrigatório para atribuição)
- `commerce.price_context` (obrigatório para payment/refund)

### Delivery Events
- `routing.shopper_id` (obrigatório)
- `commerce.order_ref` (obrigatório)
- `routing.skm_id` (opcional, mas recomendado)
