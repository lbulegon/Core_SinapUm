# Integração VitrineZap → ShopperBot Service

Guia de integração do VitrineZap com o ShopperBot Service do Core_SinapUm.

## 📋 Visão Geral

O VitrineZap consome serviços do ShopperBot via REST API. O ShopperBot fornece:
- Classificação de intenção
- Recomendação de produtos
- Tratamento de objeções
- Geração de cards
- Roteamento de conversas
- Handoff para humano

## 🔗 URL Base

```
http://shopperbot_service:7030  # Dentro da rede Docker
http://localhost:7030         # Local
https://seu-dominio.com/shopperbot  # Produção (via proxy)
```

## 🔄 Fluxos Principais

### Fluxo 1: Mensagem no Grupo

```
1. Usuário envia mensagem no grupo WhatsApp
   ↓
2. VitrineZap → POST /v1/intent/classify
   {
     "message": "quero comprar hambúrguer",
     "contexto": "group",
     "user_id": "...",
     "group_id": "...",
     "estabelecimento_id": "..."
   }
   ↓
3. ShopperBot retorna:
   {
     "intent": "buy_now",
     "confidence": 0.85,
     "urgency": 0.6,
     ...
   }
   ↓
4. VitrineZap → POST /v1/conversation/route
   ↓
5. ShopperBot retorna next_step: "group_hint" | "private_chat" | "human_handoff"
```

### Fluxo 2: Group Hint (Mostrar Cards no Grupo)

```
Se next_step == "group_hint":
  1. VitrineZap → POST /v1/recommend
     {
       "intent_payload": {...},
       "filtros": {
         "estabelecimento_id": "...",
         "max_results": 2
       }
     }
   ↓
  2. ShopperBot retorna lista de produtos recomendados
   ↓
  3. Para cada produto (máx 2):
     VitrineZap → POST /v1/creative/card
     {
       "product_id": "prod123",
       "overlay": {
         "nome": "Hambúrguer Artesanal",
         "preco": 29.90,
         "cta": "Ver produto"
       }
     }
   ↓
  4. ShopperBot retorna card_url
   ↓
  5. VitrineZap exibe cards no grupo + mensagem de convite para privado
```

### Fluxo 3: Private Chat (Conversa Individual)

```
Se next_step == "private_chat":
  1. VitrineZap inicia conversa privada
   ↓
  2. Loop de conversa:
     a. Usuário envia mensagem
     b. VitrineZap → POST /v1/intent/classify
     c. Se intent requer recomendação:
        → POST /v1/recommend
        → POST /v1/creative/card (para produtos recomendados)
     d. Se há objeção:
        → POST /v1/objection/respond
     e. Se objection.handoff_required == true:
        → POST /v1/handoff
```

### Fluxo 4: Human Handoff

```
Se next_step == "human_handoff" ou objection.handoff_required == true:
  1. VitrineZap → POST /v1/handoff
     {
       "caso": "Cliente precisa de ajuda",
       "contexto": {...},
       "suggested_human_role": "shopper",
       "user_id": "...",
       "estabelecimento_id": "..."
     }
   ↓
  2. ShopperBot retorna queue_id
   ↓
  3. VitrineZap notifica atendente humano
   ↓
  4. Atendente assume conversa
```

## 📦 Payloads de Exemplo

### Indexar Produto no Catálogo

```bash
POST /v1/catalog/index
Content-Type: application/json

{
  "product_id": "prod_123",
  "titulo": "Hambúrguer Artesanal",
  "descricao": "Hambúrguer artesanal com queijo cheddar, bacon e molho especial",
  "preco": 29.90,
  "imagens": [
    {
      "url": "https://vitrinezap.com/media/produtos/prod_123.jpg",
      "is_primary": true
    }
  ],
  "tags": ["hamburguer", "artesanal", "lanche", "queijo"],
  "categoria": "Lanches",
  "estabelecimento_id": "est_456",
  "ativo": true,
  "metadata": {
    "tempo_preparo": 15,
    "porcoes": 1
  }
}
```

### Classificar Intenção

```bash
POST /v1/intent/classify
Content-Type: application/json

{
  "message": "quero comprar esse hambúrguer agora, pode ser hoje?",
  "contexto": "group",
  "user_id": "user_789",
  "group_id": "group_001",
  "estabelecimento_id": "est_456",
  "conversation_history": []
}
```

### Recomendar Produtos

```bash
POST /v1/recommend
Content-Type: application/json

{
  "intent_payload": {
    "intent": "buy_now",
    "urgency": 0.7,
    "confidence": 0.85,
    "extracted_entities": {
      "produto": "hambúrguer",
      "categoria": null,
      "faixa_preco": null,
      "cidade": null,
      "bairro": null,
      "quantidade": null
    }
  },
  "filtros": {
    "estabelecimento_id": "est_456",
    "categoria": null,
    "faixa_preco": null,
    "max_results": 5
  }
}
```

### Gerar Card

```bash
POST /v1/creative/card
Content-Type: application/json

{
  "product_id": "prod_123",
  "overlay": {
    "nome": "Hambúrguer Artesanal",
    "preco": 29.90,
    "cta": "Quero esse!",
    "promo": "10% OFF",
    "cor_destaque": "#667eea"
  }
}
```

Resposta:
```json
{
  "card_url": "/media/cards/prod_123_abc123.png",
  "product_id": "prod_123",
  "format": "png",
  "width": 800,
  "height": 800
}
```

## 🔐 Autenticação

**Nota:** No MVP, o serviço não requer autenticação. Para produção, adicionar:
- API Key no header `X-API-Key`
- Ou autenticação via Core_SinapUm (JWT)

## 📊 Eventos e Analytics

O ShopperBot emite eventos automaticamente. Para consumir:

1. **Via Logs**: Eventos salvos em `storage/events.log` (JSON lines)
2. **Via API** (futuro): Endpoint `/v1/events` para consultar

**Formato do evento:**
```json
{
  "event_id": "uuid",
  "event_type": "INTENT_DETECTED",
  "ts": "2026-01-02T18:00:00Z",
  "request_id": "req_123",
  "user_id": "user_789",
  "group_id": "group_001",
  "estabelecimento_id": "est_456",
  "payload": {
    "intent": "buy_now",
    "confidence": 0.85
  }
}
```

## ⚠️ Tratamento de Erros

Todos os endpoints retornam erros no formato:

```json
{
  "error": "Mensagem de erro",
  "request_id": "req_123"
}
```

**Status codes:**
- `200` - Sucesso
- `400` - Bad Request (dados inválidos)
- `404` - Não encontrado
- `500` - Erro interno

## 🧪 Exemplos de cURL

### Exemplo Completo: Fluxo de Venda

```bash
# 1. Indexar produto (fazer uma vez)
curl -X POST http://localhost:7030/v1/catalog/index \
  -H "Content-Type: application/json" \
  -d '{
    "product_id": "prod_123",
    "titulo": "Hambúrguer Artesanal",
    "descricao": "Hambúrguer artesanal com queijo cheddar",
    "preco": 29.90,
    "imagens": [{"url": "https://example.com/img.jpg", "is_primary": true}],
    "tags": ["hamburguer"],
    "categoria": "Lanches",
    "estabelecimento_id": "est_456"
  }'

# 2. Mensagem do usuário → classificar intent
INTENT=$(curl -s -X POST http://localhost:7030/v1/intent/classify \
  -H "Content-Type: application/json" \
  -d '{
    "message": "quero comprar hambúrguer",
    "contexto": "group",
    "user_id": "user_789",
    "group_id": "group_001",
    "estabelecimento_id": "est_456"
  }')

echo $INTENT | jq .

# 3. Rotear conversa
ROUTE=$(curl -s -X POST http://localhost:7030/v1/conversation/route \
  -H "Content-Type: application/json" \
  -d "{
    \"intent_payload\": $(echo $INTENT),
    \"user_id\": \"user_789\",
    \"group_id\": \"group_001\",
    \"estabelecimento_id\": \"est_456\"
  }")

echo $ROUTE | jq .

# 4. Se next_step == "group_hint", recomendar e gerar cards
RECOMMEND=$(curl -s -X POST http://localhost:7030/v1/recommend \
  -H "Content-Type: application/json" \
  -d "{
    \"intent_payload\": $(echo $INTENT),
    \"filtros\": {
      \"estabelecimento_id\": \"est_456\",
      \"max_results\": 2
    }
  }")

echo $RECOMMEND | jq .

# 5. Gerar card para primeiro produto
CARD=$(curl -s -X POST http://localhost:7030/v1/creative/card \
  -H "Content-Type: application/json" \
  -d '{
    "product_id": "prod_123",
    "overlay": {
      "nome": "Hambúrguer Artesanal",
      "preco": 29.90,
      "cta": "Quero esse!"
    }
  }')

echo $CARD | jq .
```

## 🚀 Próximos Passos

1. **Integrar no VitrineZap:**
   - Adicionar cliente HTTP no VitrineZap
   - Implementar handlers para cada fluxo
   - Conectar com WhatsApp (Evolution API)

2. **Melhorias futuras:**
   - Vector DB para embeddings (busca semântica)
   - ML para intent classification
   - Analytics dashboard
   - Cache Redis para performance
   - Webhooks para eventos

3. **Produção:**
   - Autenticação
   - Rate limiting
   - Monitoring (Prometheus/Grafana)
   - Logs centralizados

