# ShopperBot Service - Quick Start

Guia rápido para iniciar o ShopperBot Service.

## 🚀 Início Rápido com Docker

```bash
cd /root/Core_SinapUm

# Build e start
docker compose up -d shopperbot_service

# Ver logs
docker compose logs -f shopperbot_service

# Verificar saúde
curl http://localhost:7030/health
```

## 📝 Testar Endpoints

### 1. Health Check

```bash
curl http://localhost:7030/health
```

### 2. Indexar Produto

```bash
curl -X POST http://localhost:7030/v1/catalog/index \
  -H "Content-Type: application/json" \
  -d '{
    "product_id": "prod_001",
    "titulo": "Hambúrguer Artesanal",
    "descricao": "Hambúrguer artesanal com queijo cheddar",
    "preco": 29.90,
    "imagens": [{"url": "https://via.placeholder.com/400", "is_primary": true}],
    "tags": ["hamburguer", "artesanal"],
    "categoria": "Lanches",
    "estabelecimento_id": "est_001"
  }'
```

### 3. Classificar Intent

```bash
curl -X POST http://localhost:7030/v1/intent/classify \
  -H "Content-Type: application/json" \
  -d '{
    "message": "quero comprar hambúrguer",
    "contexto": "group",
    "user_id": "user_001",
    "group_id": "group_001",
    "estabelecimento_id": "est_001"
  }'
```

### 4. Buscar Produtos

```bash
curl "http://localhost:7030/v1/catalog/search?q=hamburguer&estabelecimento_id=est_001&limit=5"
```

### 5. Recomendar Produtos

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
      "estabelecimento_id": "est_001",
      "max_results": 5
    }
  }'
```

### 6. Gerar Card (requer imagem)

```bash
curl -X POST http://localhost:7030/v1/creative/card \
  -H "Content-Type: application/json" \
  -d '{
    "product_id": "prod_001",
    "imagem_original_url": "https://via.placeholder.com/800",
    "overlay": {
      "nome": "Hambúrguer Artesanal",
      "preco": 29.90,
      "cta": "Quero esse!"
    }
  }'
```

## 📚 Documentação Completa

- [README.md](README.md) - Documentação completa
- [docs/vitrinezap_integration.md](../../docs/vitrinezap_integration.md) - Guia de integração

## 🔧 Desenvolvimento Local

```bash
cd /root/Core_SinapUm/services/shopperbot_service

# Criar venv
python3 -m venv venv
source venv/bin/activate

# Instalar dependências
pip install -r requirements.txt

# Rodar servidor
uvicorn app.main:app --host 0.0.0.0 --port 7030 --reload
```

## 🧪 Testes

```bash
cd /root/Core_SinapUm/services/shopperbot_service

# Instalar dependências de teste
pip install -r requirements.txt

# Rodar testes
pytest

# Com coverage
pytest --cov=app --cov-report=html
```

## 🔍 Swagger/OpenAPI

Acesse a documentação interativa:
- http://localhost:7030/docs
- http://localhost:7030/redoc

