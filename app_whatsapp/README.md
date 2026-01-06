# WhatsApp Gateway

Gateway plugável para integração WhatsApp com providers múltiplos.

## Providers

- **simulated**: Provider simulado para desenvolvimento (padrão)
- **cloud**: WhatsApp Cloud API (Fase A2)
- **baileys**: Baileys direto (Fase A2)
- **evolution**: Evolution API (Fase B)

## Configuração

```bash
export WHATSAPP_PROVIDER=simulated
```

Ou no `settings.py`:
```python
WHATSAPP_PROVIDER = 'simulated'
```

## Endpoints

### Principais

- `POST /api/whatsapp/instances/` - Criar instância
- `GET /api/whatsapp/instances/{key}/qr/` - Obter QR
- `POST /api/whatsapp/send/` - Enviar mensagem
- `POST /api/whatsapp/inbound/` - Webhook universal
- `GET /api/whatsapp/health/` - Health check

### Simulação (apenas simulated)

- `POST /api/whatsapp/instances/{key}/simulate/scan/` - Simular scan QR
- `POST /api/whatsapp/instances/{key}/simulate/disconnect/` - Simular desconexão
- `POST /api/whatsapp/instances/{key}/simulate/inbound/` - Simular mensagem recebida

## Eventos

Todos os eventos são persistidos em `AppWhatsappEvent` e logados.

**Tipos:**
- `INSTANCE_CREATED` - Instância criada
- `QR_UPDATED` - QR code atualizado
- `CONNECTED` - Conectado ao WhatsApp
- `DISCONNECTED` - Desconectado
- `MESSAGE_IN` - Mensagem recebida
- `MESSAGE_OUT` - Mensagem enviada
- `DELIVERY` - Entrega confirmada
- `ERROR` - Erro ocorrido

## Exemplo de Uso

### Criar Instância

```bash
curl -X POST http://localhost:8000/api/whatsapp/instances/ \
  -H "Content-Type: application/json" \
  -d '{"instance_key": "test_123"}'
```

### Obter QR Code

```bash
curl http://localhost:8000/api/whatsapp/instances/test_123/qr/
```

### Simular Scan (apenas simulated)

```bash
curl -X POST http://localhost:8000/api/whatsapp/instances/test_123/simulate/scan/
```

### Simular Mensagem Recebida

```bash
curl -X POST http://localhost:8000/api/whatsapp/instances/test_123/simulate/inbound/ \
  -H "Content-Type: application/json" \
  -d '{"from_number": "5511999999999", "text": "Olá", "shopper_id": "shopper_123"}'
```

### Enviar Mensagem

```bash
curl -X POST http://localhost:8000/api/whatsapp/send/ \
  -H "Content-Type: application/json" \
  -d '{
    "instance_key": "test_123",
    "to": "5511999999999",
    "payload": {"text": "Olá, como posso ajudar?"}
  }'
```

## Estrutura

```
app_whatsapp/
  domain/          # Contratos e eventos canônicos
  providers/       # Implementações dos providers
  services/        # Router e EventBus
  api/             # Endpoints DRF
  models.py        # AppWhatsappEvent, AppWhatsappInstance
```

## Migrations

```bash
python manage.py makemigrations app_whatsapp
python manage.py migrate app_whatsapp
```

## Testes

```bash
python manage.py test app_whatsapp
```
