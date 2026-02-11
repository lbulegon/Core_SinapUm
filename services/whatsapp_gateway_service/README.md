# WhatsApp Gateway Service

Microserviço WhatsApp Gateway usando Node.js + Baileys, derivado do projeto `bot-do-mago`.

## 📋 Visão Geral

Este serviço encapsula a funcionalidade do WhatsApp usando Baileys como um microserviço HTTP REST, permitindo que o Core_SinapUm (Python) gerencie conexões WhatsApp de forma centralizada.

**Arquitetura:**
- **Core_SinapUm (Python)**: Orquestrador central
- **WhatsApp Gateway Service (Node.js)**: Gateway WhatsApp periférico

## 🚀 Estrutura

```
services/whatsapp_gateway_service/
├── Dockerfile
├── package.json
├── .dockerignore
├── README.md
└── src/
    ├── index.js          # Bootstrap do serviço
    ├── wa.js             # Lógica Baileys (adaptada do bot-do-mago)
    ├── routes.js         # API HTTP (Express)
    ├── auth.js           # Autenticação Baileys
    ├── events.js         # Configuração de eventos
    └── utils/
        ├── filterLogs.js
        ├── waitMessage.js
        └── auditEvents.js
```

## 🔧 Configuração

### Variáveis de Ambiente

No `.env` do Core_SinapUm:

```bash
# Porta do serviço
SINAPUM_WHATSAPP_GATEWAY_PORT=8008

# API Key para autenticação
SINAPUM_WHATSAPP_GATEWAY_API_KEY=<SEGREDO_FORTE>

# URL do serviço (interna Docker)
SINAPUM_WHATSAPP_GATEWAY_URL=http://whatsapp_gateway_service:8007

# URL base do Core_SinapUm
SINAPUM_CORE_BASE_URL=http://mcp_sinapum_web:8000

# Path do webhook
SINAPUM_WHATSAPP_WEBHOOK_PATH=/webhooks/whatsapp

# URL completa do webhook
SINAPUM_WHATSAPP_WEBHOOK_URL=${SINAPUM_CORE_BASE_URL}${SINAPUM_WHATSAPP_WEBHOOK_PATH}

# Conectar automaticamente ao iniciar (opcional)
SINAPUM_WHATSAPP_AUTO_CONNECT=false
```

### Docker Compose

O serviço já está configurado no `docker-compose.yml` do Core_SinapUm:

```yaml
whatsapp_gateway_service:
  build: ./services/whatsapp_gateway_service
  container_name: whatsapp_gateway_service
  restart: unless-stopped
  ports:
    - "${SINAPUM_WHATSAPP_GATEWAY_PORT:-8007}:8007"
  environment:
    - PORT=8007
    - API_KEY=${SINAPUM_WHATSAPP_GATEWAY_API_KEY}
    - WEBHOOK_URL=${SINAPUM_WHATSAPP_WEBHOOK_URL}
    - AUTH_DIR=/data/auth
    - AUTO_CONNECT=${SINAPUM_WHATSAPP_AUTO_CONNECT:-false}
  volumes:
    - wa_auth:/data/auth
  networks:
    - mcp_network
```

## 📡 API Endpoints

### Health Check (Aberto)

```http
GET /health
```

**Resposta:**
```json
{
  "status": "ok",
  "whatsapp": {
    "status": "connected",
    "connected": true
  },
  "timestamp": "2025-02-04T12:00:00.000Z"
}
```

### Status (Requer API Key)

```http
GET /v1/status
Headers:
  X-API-Key: <API_KEY>
```

**Resposta:**
```json
{
  "connection": "connected",
  "qr_available": false,
  "socket_active": true
}
```

### QR Code (Requer API Key)

```http
GET /v1/qr
Headers:
  X-API-Key: <API_KEY>
```

**Resposta:** Imagem PNG do QR code

### Conectar (Requer API Key)

```http
POST /v1/connect
Headers:
  X-API-Key: <API_KEY>
```

**Resposta:**
```json
{
  "success": true,
  "message": "Conexão iniciada",
  "status": "connecting"
}
```

### Desconectar (Requer API Key)

```http
POST /v1/disconnect
Headers:
  X-API-Key: <API_KEY>
```

### Resetar Sessão (Requer API Key)

```http
POST /v1/session/reset
Headers:
  X-API-Key: <API_KEY>
```

### Enviar Texto (Requer API Key)

```http
POST /v1/send/text
Headers:
  X-API-Key: <API_KEY>
Content-Type: application/json

{
  "to": "5511999999999",
  "text": "Mensagem de teste"
}
```

**Resposta:**
```json
{
  "success": true,
  "message_id": "3EB0123456789ABCDEF",
  "to": "5511999999999@s.whatsapp.net",
  "status": "sent"
}
```

### Enviar Imagem (Requer API Key)

```http
POST /v1/send/image
Headers:
  X-API-Key: <API_KEY>
Content-Type: application/json

{
  "to": "5511999999999",
  "image_path": "/path/to/image.jpg",
  "caption": "Legenda opcional"
}
```

Ou usando URL:
```json
{
  "to": "5511999999999",
  "image_url": "https://example.com/image.jpg",
  "caption": "Legenda opcional"
}
```

Ou usando base64:
```json
{
  "to": "5511999999999",
  "image_base64": "iVBORw0KGgoAAAANS...",
  "caption": "Legenda opcional"
}
```

### Enviar Documento (Requer API Key)

```http
POST /v1/send/document
Headers:
  X-API-Key: <API_KEY>
Content-Type: application/json

{
  "to": "5511999999999",
  "document_path": "/path/to/document.pdf",
  "filename": "documento.pdf",
  "caption": "Legenda opcional"
}
```

## 🔗 Webhook

O serviço envia eventos automaticamente para o webhook configurado:

**URL:** `${SINAPUM_WHATSAPP_WEBHOOK_URL}`

**Formato:**
```json
{
  "event_type": "message|qr|connected|disconnected",
  "payload": { ... },
  "ts": "2025-02-04T12:00:00.000Z"
}
```

### Evento: message

```json
{
  "event_type": "message",
  "payload": {
    "id": "3EB0123456789ABCDEF",
    "from": "5511999999999@s.whatsapp.net",
    "isFromMe": false,
    "number": "5511999999999",
    "text": "texto da mensagem",
    "raw": { ... }
  },
  "ts": "2025-02-04T12:00:00.000Z"
}
```

### Evento: qr

```json
{
  "event_type": "qr",
  "payload": {
    "qr": "data:image/png;base64,iVBORw0KGgoAAAANS..."
  },
  "ts": "2025-02-04T12:00:00.000Z"
}
```

### Evento: connected

```json
{
  "event_type": "connected",
  "payload": {},
  "ts": "2025-02-04T12:00:00.000Z"
}
```

### Evento: disconnected

```json
{
  "event_type": "disconnected",
  "payload": {
    "shouldReconnect": true
  },
  "ts": "2025-02-04T12:00:00.000Z"
}
```

## 🐍 Uso no Core_SinapUm (Python)

### Cliente

```python
from core.services.whatsapp_gateway_client import get_whatsapp_gateway_client

client = get_whatsapp_gateway_client()

# Verificar saúde
health = client.healthcheck()

# Obter status
status = client.get_status()

# Obter QR code
qr_image = client.get_qr_code()

# Conectar
result = client.connect()

# Enviar mensagem
result = client.send_text("5511999999999", "Mensagem de teste")

# Enviar imagem
result = client.send_image(
    "5511999999999",
    image_path="/path/to/image.jpg",
    caption="Legenda"
)
```

### Webhook Handler

O webhook está configurado em:
- **URL:** `/webhooks/whatsapp/`
- **Handler:** `core.services.whatsapp.webhook_handler.handle_incoming_whatsapp_event`

## 🏗️ Build e Deploy

### Build

```bash
cd /root/Core_SinapUm
docker-compose build whatsapp_gateway_service
```

### Iniciar

```bash
docker-compose up -d whatsapp_gateway_service
```

### Logs

```bash
docker logs -f whatsapp_gateway_service
```

### Parar

```bash
docker-compose stop whatsapp_gateway_service
```

## 📝 Notas

- **Sessão**: As credenciais são armazenadas em `/data/auth` (volume Docker `wa_auth`)
- **Reconexão**: O serviço reconecta automaticamente em caso de desconexão (exceto se logout manual)
- **QR Code**: Gerado automaticamente quando necessário para autenticação
- **Webhook**: Eventos são enviados automaticamente para o Core_SinapUm

## 🔒 Segurança

- Todos os endpoints (exceto `/health`) requerem `X-API-Key` header
- API Key deve ser configurada via variável de ambiente
- Webhook valida API Key antes de processar eventos

## 📚 Referências

- [Baileys](https://github.com/WhiskeySockets/Baileys)
- [Projeto Original (bot-do-mago)](/root/Source/bot-do-mago)
