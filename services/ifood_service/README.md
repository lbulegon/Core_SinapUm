# iFood Service

Serviço FastAPI para integração OAuth 2.0 e sincronização de dados do iFood com o Core_SinapUm.

## Arquitetura

- **Control Plane (Core_SinapUm)**: Django app `app_ifood_integration` gerencia lojas, tokens e dados normalizados
- **Data Plane (ifood_service)**: FastAPI service que executa OAuth e sincroniza dados

## Variáveis de Ambiente

```bash
# OAuth iFood
IFOOD_CLIENT_ID=seu_client_id
IFOOD_CLIENT_SECRET=seu_client_secret
IFOOD_AUTH_BASE_URL=https://auth.ifood.com.br
IFOOD_API_BASE_URL=https://merchant-api.ifood.com.br
IFOOD_REDIRECT_URI=http://localhost:7020/oauth/callback

# Core SinapUm
CORE_INTERNAL_BASE_URL=http://web:5000
INTERNAL_API_KEY=sua_chave_interna

# Redis (opcional)
REDIS_URL=redis://redis:6379/0
```

## Endpoints

### Health Check
```
GET /health
```

### OAuth
```
GET /oauth/authorize-link?store_id=1&state=optional
GET /oauth/callback?code=...&state=...
```

### Sincronização
```
POST /sync/orders
Body: {
    "store_id": 1,
    "date_from": "2024-01-01",
    "date_to": "2024-01-31"
}

POST /sync/finance
Body: {
    "store_id": 1,
    "period": "2024-01"
}
```

## Fluxo de Integração

1. **Cadastrar Loja no Core** (via Django Admin)
   - Criar `IfoodStore` com `ifood_merchant_id`

2. **Gerar Link de Autorização**
   ```
   GET /oauth/authorize-link?store_id=1
   ```

3. **Autorizar no Portal iFood**
   - Usuário acessa URL retornada
   - Autoriza acesso no Portal do Parceiro

4. **Callback OAuth**
   - iFood redireciona para `/oauth/callback?code=...`
   - Service troca code por tokens e salva no Core

5. **Sincronizar Dados**
   ```
   POST /sync/orders {"store_id": 1, "date_from": "2024-01-01"}
   POST /sync/finance {"store_id": 1, "period": "2024-01"}
   ```

## Executar Localmente

```bash
cd /root/Core_SinapUm/services/ifood_service
pip install -r requirements.txt
uvicorn main:app --host 0.0.0.0 --port 7020
```

## Docker

```bash
docker build -t ifood_service .
docker run -p 7020:7020 --env-file .env ifood_service
```

