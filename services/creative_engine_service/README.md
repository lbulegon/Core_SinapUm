# Creative Engine Service

Motor Omneky-like para gerar criativos (cards + copy + discursos) para shoppers.

## Visão Geral

O Creative Engine Service gera criativos adaptados para diferentes canais (WhatsApp status/grupo/1:1), cria variações estratégicas, registra performance baseada em eventos reais e aplica aprendizado para otimizar recomendações.

## Arquitetura

```
services/creative_engine_service/
├── contracts.py          # Contratos públicos
├── engine.py             # Orquestrador principal
├── events.py             # Eventos canônicos
├── generators/           # Geradores (text, image, discourse)
├── strategies/           # Estratégias (price, benefit, urgency, scarcity, social_proof)
├── adapters/             # Adaptadores (whatsapp, generic)
└── learning/             # Aprendizado (scorer, optimizer)
```

## Endpoints

### POST /api/creative-engine/generate

Gera criativo principal para produto e shopper.

**Request:**
```json
{
  "product_id": "123",
  "shopper_id": "shopper_456",
  "channel": "group",
  "locale": "pt-BR",
  "tone": "direto",
  "time_of_day": "afternoon",
  "stock_level": "normal",
  "price_sensitivity": "medium"
}
```

**Response:**
```json
{
  "creative_id": "uuid",
  "variants": [
    {
      "variant_id": "uuid",
      "strategy": "price",
      "channel": "group",
      "image_url": "http://...",
      "text_short": "...",
      "text_medium": "...",
      "text_long": "...",
      "discourse": {...},
      "ctas": ["Saiba mais"]
    }
  ],
  "recommended_variant_id": "uuid"
}
```

### POST /api/creative-engine/{creative_id}/variants

Gera variantes de um criativo usando estratégias específicas.

**Request:**
```json
{
  "strategies": ["price", "benefit", "urgency"],
  "channel": "group",
  "tone": "direto"
}
```

### POST /api/creative-engine/variants/{variant_id}/adapt

Adapta variante para canal específico.

**Request:**
```json
{
  "channel": "status",
  "tone": "direto"
}
```

### POST /api/creative-engine/performance

Registra evento de performance.

**Request:**
```json
{
  "variant_id": "uuid",
  "product_id": "123",
  "shopper_id": "shopper_456",
  "type": "VIEWED",
  "data": {}
}
```

### GET /api/creative-engine/recommend

Recomenda próximo criativo baseado em aprendizado.

**Query Params:**
- `shopper_id`: ID do shopper
- `product_id`: ID do produto
- `channel`: Canal (status|group|private)
- `tone`: Tom (direto|elegante|popular|premium|urgente)

## Eventos Canônicos

Todos os eventos são emitidos e logados:

- `CREATIVE_GENERATED` - Criativo gerado
- `CREATIVE_VARIANT_GENERATED` - Variante gerada
- `CREATIVE_ADAPTED` - Criativo adaptado
- `CREATIVE_SENT` - Criativo enviado
- `CREATIVE_VIEWED` - Criativo visualizado
- `CREATIVE_RESPONDED` - Resposta recebida
- `CREATIVE_INTERESTED` - Interesse demonstrado
- `CREATIVE_ORDERED` - Pedido realizado
- `CREATIVE_CONVERTED` - Conversão realizada
- `CREATIVE_IGNORED` - Criativo ignorado

## Estratégias

### Price
Foco em preço e valor. Melhor para canais de grupo com alta sensibilidade a preço.

### Benefit
Foco em benefícios e qualidade. Melhor para 1:1 e canais premium.

### Urgency
Foco em tempo limitado. Melhor para status e campanhas temporárias.

### Scarcity
Foco em estoque limitado. Melhor quando stock_level é "low".

### Social Proof
Foco em popularidade e recomendações. Melhor com histórico de performance.

## Como Integrar o VitrineZap

1. **Gerar criativo:**
   ```javascript
   POST /api/creative-engine/generate
   {
     product_id: "123",
     shopper_id: "shopper_456",
     channel: "group",
     tone: "direto"
   }
   ```

2. **Usar variante recomendada:**
   ```javascript
   const variant = response.variants.find(
     v => v.variant_id === response.recommended_variant_id
   );
   ```

3. **Renderizar no WhatsApp:**
   - Status: `variant.text_short` + `variant.image_url`
   - Grupo: `variant.text_medium` + `variant.image_url`
   - 1:1: `variant.text_long` + `variant.discourse`

4. **Registrar performance:**
   ```javascript
   POST /api/creative-engine/performance
   {
     variant_id: variant.variant_id,
     type: "VIEWED",
     product_id: "123",
     shopper_id: "shopper_456"
   }
   ```

## Como Evoluir para IA

### Pontos de Extensão

1. **Geradores:**
   - `generators/text.py`: Substituir templates por LLM
   - `generators/image.py`: Adicionar geração por IA (DALL-E, Midjourney)
   - `generators/discourse.py`: Usar LLM para argumentos

2. **Estratégias:**
   - Adicionar estratégias baseadas em ML
   - Usar embeddings para similaridade de produtos

3. **Optimizer:**
   - Substituir heurísticas por modelo de ML
   - Usar reinforcement learning para ajuste de pesos

4. **Scorer:**
   - Adicionar predição de conversão
   - Usar modelos de classificação

## Configuração

Nenhuma configuração adicional necessária. O serviço usa os modelos Django existentes (`Produto`, `Shopper`).

## Testes

```bash
python manage.py test services.creative_engine_service.tests
```

## Persistência

Models em `app_creative_engine/models.py`:
- `CreativeAsset`: Assets de criativo
- `CreativePerformance`: Eventos de performance
- `CreativeScore`: Scores agregados

## Logs

Todos os eventos são logados com:
- `[Creative Engine]` prefix
- Shopper ID, Product ID, Creative ID
- Correlation ID para rastreamento

## Exemplo Completo

```python
from services.creative_engine_service.engine import CreativeEngine
from services.creative_engine_service.contracts import CreativeContext

engine = CreativeEngine()

context = CreativeContext(
    channel="group",
    locale="pt-BR",
    tone="direto",
    stock_level="normal"
)

result = engine.generate_creative(
    product_id="123",
    shopper_id="shopper_456",
    context=context
)

# Usar variante recomendada
variant = next(
    v for v in result.variants 
    if v.variant_id == result.recommended_variant_id
)

print(variant.text_medium)
print(variant.image_url)
```
