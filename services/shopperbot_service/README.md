# ShopperBot Service - IA Vendedora para VitrineZap

Sistema de IA vendedora nativo do Évora/VitrineZap. Fornece serviços de classificação de intenção, recomendação de produtos, tratamento de objeções, geração de cards e roteamento de conversas.

## 🏗️ Arquitetura

```
shopperbot_service/
├── app/
│   ├── main.py              # FastAPI app principal
│   ├── routers/             # Endpoints REST
│   ├── services/            # Lógica de negócio
│   ├── schemas/             # Modelos Pydantic
│   ├── storage/             # Abstração de persistência
│   ├── events/              # Emissão de eventos
│   └── utils/               # Config, logging, etc
├── tests/                   # Testes pytest
├── storage/                 # Dados persistidos (cards, logs)
├── Dockerfile
├── docker-compose.yml
└── requirements.txt
```

## 🚀 Início Rápido

### Local (desenvolvimento)

```bash
cd /root/Core_SinapUm/services/shopperbot_service

# Criar venv
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# ou: venv\Scripts\activate  # Windows

# Instalar dependências
pip install -r requirements.txt

# Rodar servidor
uvicorn app.main:app --host 0.0.0.0 --port 7030 --reload
```

### Docker

```bash
cd /root/Core_SinapUm

# Build e start
docker compose up -d shopbot_service

# Ver logs
docker compose logs -f shopperbot_service
```

## 📡 Endpoints

Todos os endpoints estão versionados em `/v1/`.

### Health Check

```bash
curl http://localhost:7030/health
```

### A) Catalog Index

#### Indexar produto

```bash
curl -X POST http://localhost:7030/v1/catalog/index \
  -H "Content-Type: application/json" \
  -d '{
    "product_id": "prod123",
    "titulo": "Hambúrguer Artesanal",
    "descricao": "Hambúrguer artesanal com queijo cheddar",
    "preco": 29.90,
    "imagens": [
      {"url": "https://example.com/img.jpg", "is_primary": true}
    ],
    "tags": ["hamburguer", "artesanal", "lanche"],
    "categoria": "Lanches",
    "estabelecimento_id": "est123"
  }'
```

#### Buscar produtos

```bash
curl "http://localhost:7030/v1/catalog/search?q=hamburguer&estabelecimento_id=est123&limit=10"
```

### B) Intent Classification

```bash
curl -X POST http://localhost:7030/v1/intent/classify \
  -H "Content-Type: application/json" \
  -d '{
    "message": "quero comprar esse hambúrguer agora",
    "contexto": "group",
    "user_id": "user123",
    "group_id": "group123",
    "estabelecimento_id": "est123"
  }'
```

**Resposta:**
```json
{
  "intent": "buy_now",
  "urgency": 0.6,
  "confidence": 0.85,
  "extracted_entities": {
    "produto": null,
    "categoria": null,
    "faixa_preco": null,
    "cidade": null,
    "bairro": null,
    "quantidade": null
  },
  "reasoning": "Intent detectado: buy_now (confidence: 0.85)"
}
```

### C) Recommendation

```bash
curl -X POST http://localhost:7030/v1/recommend \
  -H "Content-Type: application/json" \
  -d '{
    "intent_payload": {
      "intent": "buy_now",
      "urgency": 0.6,
      "confidence": 0.85,
      "extracted_entities": {}
    },
    "filtros": {
      "estabelecimento_id": "est123",
      "max_results": 5
    }
  }'
```

### D) Objection Response

```bash
curl -X POST http://localhost:7030/v1/objection/respond \
  -H "Content-Type: application/json" \
  -d '{
    "message": "muito caro esse produto",
    "intent": "price_check",
    "product_id": "prod123"
  }'
```

### E) Creative Card

```bash
curl -X POST http://localhost:7030/v1/creative/card \
  -H "Content-Type: application/json" \
  -d '{
    "product_id": "prod123",
    "overlay": {
      "nome": "Hambúrguer Artesanal",
      "preco": 29.90,
      "cta": "Ver produto",
      "promo": "10% OFF"
    }
  }'
```

### F) Conversation Routing

```bash
curl -X POST http://localhost:7030/v1/conversation/route \
  -H "Content-Type: application/json" \
  -d '{
    "intent_payload": {
      "intent": "buy_now",
      "urgency": 0.6,
      "confidence": 0.85,
      "extracted_entities": {}
    },
    "user_id": "user123",
    "group_id": "group123",
    "estabelecimento_id": "est123"
  }'
```

### G) Handoff

```bash
curl -X POST http://localhost:7030/v1/handoff \
  -H "Content-Type: application/json" \
  -d '{
    "caso": "Cliente precisa de ajuda com pedido",
    "contexto": {},
    "suggested_human_role": "shopper",
    "user_id": "user123",
    "estabelecimento_id": "est123",
    "urgency": 0.7
  }'
```

## 🔄 Fluxo de Integração com VitrineZap

### 1. Mensagem no grupo

```bash
# 1. Classificar intenção
INTENT_RESPONSE = POST /v1/intent/classify

# 2. Rotear conversa
ROUTE_RESPONSE = POST /v1/conversation/route
```

### 2. Se group_hint → mostrar cards

```bash
# 3. Recomendar produtos
RECOMMEND_RESPONSE = POST /v1/recommend

# 4. Gerar cards (até 2)
for product in RECOMMEND_RESPONSE.products[:2]:
    CARD_RESPONSE = POST /v1/creative/card
    # Exibir card no grupo
```

### 3. Se private_chat → conversa individual

```bash
# Loop: enquanto conversa ativa
# - Classificar intent
# - Recomendar produtos
# - Tratar objeções
OBJECTION_RESPONSE = POST /v1/objection/respond
```

### 4. Se human_handoff → conectar humano

```bash
HANDOFF_RESPONSE = POST /v1/handoff
```

## 📊 Eventos e Analytics

Eventos são emitidos automaticamente e salvos em:
- Logs estruturados (JSON)
- Arquivo: `storage/events.log`

**Tipos de eventos:**
- `INTENT_DETECTED`
- `PRODUCT_RECOMMENDED`
- `OBJECTION_HANDLED`
- `CARD_GENERATED`
- `PRIVATE_CHAT_STARTED`
- `HUMAN_HANDOFF`

## 🔧 Configuração

Variáveis de ambiente:

```bash
PORT=7030                    # Porta do serviço
DEBUG=False                  # Modo debug
STORAGE_PATH=./storage       # Caminho para dados
LOG_LEVEL=INFO              # Nível de log
DATABASE_URL=                # Opcional: DB para analytics
```

## 🧪 Testes

```bash
# Rodar testes
pytest

# Com coverage
pytest --cov=app --cov-report=html
```

## 📝 Notas de Implementação

### Catalog Storage
- Usa SQLite + FTS5 para busca textual
- Interface preparada para migrar para vector DB (embeddings)
- Por enquanto: busca por palavras-chave e BM25

### Intent Classification
- Baseado em palavras-chave (pode ser expandido com ML)
- Classes: buy_now, compare, price_check, availability, urgent, gift, support, just_browsing

### Creative Cards
- **Preserva foto original** - não gera imagem por IA
- Adiciona overlays discretos com PIL/Pillow
- Mantém autenticidade da foto amadora

### Routing
- Lógica baseada em regras (pode ser expandida com ML)
- Decisões: group_hint, private_chat, human_handoff

## 🚢 Deploy

### Docker Compose

Já integrado no `docker-compose.yml` principal do Core_SinapUm.

```bash
cd /root/Core_SinapUm
docker compose up -d shopbot_service
```

### Standalone

```bash
cd services/shopperbot_service
docker build -t shopperbot:latest .
docker run -d -p 7030:7030 -v $(pwd)/storage:/app/storage shopperbot:latest
```

## 📚 Documentação da API

Swagger/OpenAPI disponível em:
- http://localhost:7030/docs
- http://localhost:7030/redoc

## ✅ Checklist de Integração

- [x] Serviço criado e funcional
- [x] Todos os endpoints implementados
- [x] Storage de catálogo funcionando
- [x] Eventos sendo emitidos
- [x] Logging estruturado
- [x] Dockerfile e docker-compose
- [x] Testes básicos
- [x] Documentação completa
- [ ] Integração com VitrineZap (próximo passo)
- [ ] Métricas e monitoring (futuro)
- [ ] Vector DB para embeddings (futuro)

