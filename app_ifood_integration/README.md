# app_ifood_integration

Django app para integração iFood → MrFoo Dashboard.

## Models

### IfoodStore
Representa uma loja/estabelecimento no iFood.

**Campos:**
- `nome`: Nome da loja
- `cnpj`: CNPJ (opcional)
- `ifood_merchant_id`: ID único no iFood (obrigatório, único)
- `ativo`: Status de ativação

### IfoodOAuthToken
Tokens OAuth 2.0 por loja.

**Campos:**
- `store`: OneToOne com IfoodStore
- `access_token`: Access token (criptografado em produção)
- `refresh_token`: Refresh token (criptografado em produção)
- `expires_at`: Data de expiração
- `scope`: Escopos OAuth

**Métodos:**
- `is_expired()`: Verifica se token está expirado
- `needs_refresh(buffer_minutes=5)`: Verifica se precisa renovar

### IfoodSyncRun
Histórico de execuções de sincronização.

**Campos:**
- `store`: ForeignKey para IfoodStore
- `kind`: Tipo ('orders', 'financial', 'catalog')
- `started_at`, `finished_at`: Timestamps
- `ok`: Sucesso
- `items_ingested`: Quantidade processada
- `error`: Mensagem de erro
- `metadata`: JSON com metadados adicionais

### MrfooOrder
Pedidos normalizados para consumo do Dashboard MrFoo.

**Campos:**
- `store`: ForeignKey para IfoodStore
- `order_id`: ID único do pedido no iFood
- `created_at`: Data/hora do pedido
- `status`: Status do pedido
- `total_value`: Valor total
- `channel`: Canal de origem ('ifood')
- `raw_json`: Dados brutos completos

### MrfooPayout
Repasses financeiros normalizados para consumo do Dashboard MrFoo.

**Campos:**
- `store`: ForeignKey para IfoodStore
- `payout_id`: ID único do repasse
- `reference_period`: Período (YYYY-MM)
- `gross`, `fees`, `net`: Valores financeiros
- `channel`: Canal de origem
- `raw_json`: Dados brutos completos

## API Interna

Todos os endpoints requerem autenticação via `Authorization: Bearer {INTERNAL_API_KEY}`.

### Lojas
- `GET /internal/ifood/stores` - Lista lojas
- `GET /internal/ifood/stores/{id}/status` - Status detalhado
- `POST /internal/ifood/stores/{id}/tokens` - Salvar tokens OAuth
- `POST /internal/ifood/stores/{id}/sync/orders` - Solicitar sync de pedidos
- `POST /internal/ifood/stores/{id}/sync/finance` - Solicitar sync financeiro

### Sincronização
- `POST /internal/ifood/stores/{id}/sync-runs` - Criar registro de sync
- `PATCH /internal/ifood/sync-runs/{id}` - Atualizar registro de sync

### Dados Normalizados (MrFoo)
- `GET /internal/mrfoo/orders?store_id=&date_from=&date_to=` - Listar pedidos
- `POST /internal/mrfoo/orders/save` - Salvar pedido
- `GET /internal/mrfoo/payouts?store_id=&period=` - Listar repasses
- `POST /internal/mrfoo/payouts/save` - Salvar repasse

## Variáveis de Ambiente

```bash
INTERNAL_API_KEY=chave_secreta_para_api_interna
```

## Migrations

```bash
python manage.py makemigrations app_ifood_integration
python manage.py migrate app_ifood_integration
```

## Admin

Todos os models estão registrados no Django Admin com:
- Filtros e buscas
- Exibição de status de tokens
- Histórico de sincronizações
- Ações para disparar syncs

