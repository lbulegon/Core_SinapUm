# Inventário de Endpoints Existentes

## Core_SinapUm - Endpoints WhatsApp/Evolution

### URLs (setup/urls.py)
| Endpoint | Método | View | Descrição |
|----------|--------|------|-----------|
| `/whatsapp/` | GET | `whatsapp_connect` | Página para conectar WhatsApp |
| `/whatsapp/api/create-instance/` | POST | `whatsapp_create_instance` | Criar instância Evolution |
| `/whatsapp/api/get-qrcode/` | GET | `whatsapp_get_qrcode` | Obter QR Code |
| `/whatsapp/api/get-status/` | GET | `whatsapp_get_status` | Status da instância |
| `/whatsapp/api/delete-instance/` | POST | `whatsapp_delete_instance` | Deletar instância |
| `/whatsapp/api/restart-instance/` | POST | `whatsapp_restart_instance` | Reiniciar instância |

### Outros Endpoints Core
| Endpoint | Método | Descrição |
|----------|--------|-----------|
| `/core/` | - | MCP Tool Registry |
| `/api/v1/analyze-product-image` | POST | Análise de imagens |
| `/health` | GET | Health check |

---

## Évora/VitrineZap - Endpoints WhatsApp/Evolution

### URLs (app_whatsapp_integration/urls.py)
| Endpoint | Método | View | Descrição |
|----------|--------|------|-----------|
| `/api/whatsapp/webhook/evolution/` | POST/GET/PUT | `webhook_evolution_api` | **Webhook Evolution API** |
| `/api/whatsapp/webhook-from-gateway/` | POST | `webhook_from_gateway` | Webhook do gateway |
| `/api/whatsapp/send/` | POST | `send_message` | Enviar mensagem texto |
| `/api/whatsapp/send-product/` | POST | `send_product` | Enviar produto |
| `/api/whatsapp/status/` | GET | `instance_status` | Status da instância |
| `/api/whatsapp/qrcode/` | GET/POST | `get_qrcode` | Obter QR Code |
| `/api/whatsapp/connect/` | POST | `connect_instance` | Criar instância e obter QR |

### Outros Endpoints Évora
| Endpoint | Método | Descrição |
|----------|--------|-----------|
| `/health/` | GET | Health check Railway |
| `/admin/` | - | Django Admin |

---

## Detalhamento dos Endpoints Críticos

### 1. Webhook Evolution API (Évora)
**Endpoint:** `/api/whatsapp/webhook/evolution/`  
**Método:** POST, GET, PUT  
**View:** `webhook_evolution_api`

**Processamento atual:**
- Recebe eventos da Evolution API
- Processa eventos `messages.upsert`
- Processa eventos `qrcode.updated`
- Cria/atualiza `EvolutionInstance`
- Cria/atualiza `WhatsAppContact`
- Salva `EvolutionMessage` e `WhatsAppMessageLog`
- Processa via `WhatsAppFlowEngine` (grupo ou privado)
- Envia respostas automáticas

**⚠️ RISCO:** Este endpoint já está ativo e processando mensagens.  
**⚠️ AÇÃO:** Não remover ou modificar sem criar novo endpoint primeiro.

---

### 2. Enviar Mensagem (Évora)
**Endpoint:** `/api/whatsapp/send/`  
**Método:** POST  
**View:** `send_message`

**Payload:**
```json
{
  "phone": "+5511999999999",
  "message": "Texto da mensagem"
}
```

**Processamento:**
- Usa `EvolutionAPIService.send_text_message()`
- Retorna sucesso/erro

---

### 3. Enviar Produto (Évora)
**Endpoint:** `/api/whatsapp/send-product/`  
**Método:** POST  
**View:** `send_product`

**Payload:**
```json
{
  "phone": "+5511999999999",
  "product_id": 123,
  "product_data": {...},
  "image_url": "https://..."
}
```

---

### 4. Criar Instância (Core)
**Endpoint:** `/whatsapp/api/create-instance/`  
**Método:** POST  
**View:** `whatsapp_create_instance`

**Processamento:**
- Cria instância na Evolution API
- Retorna status

---

### 5. Obter QR Code (Core)
**Endpoint:** `/whatsapp/api/get-qrcode/`  
**Método:** GET  
**View:** `whatsapp_get_qrcode`

**Processamento:**
- Obtém QR Code da Evolution API
- Retorna base64 ou URL

---

## Fluxos Existentes

### Fluxo de Recebimento de Mensagem (Évora)
1. Evolution API → `/api/whatsapp/webhook/evolution/`
2. Parse do evento `messages.upsert`
3. Cria/atualiza `EvolutionInstance`
4. Cria/atualiza `WhatsAppContact`
5. Salva `EvolutionMessage` e `WhatsAppMessageLog`
6. Processa via `WhatsAppFlowEngine`:
   - Se grupo: `processar_mensagem_grupo()`
   - Se privado: `processar_mensagem_privada()`
7. Envia resposta automática via Evolution

### Fluxo de Envio de Mensagem (Évora)
1. POST `/api/whatsapp/send/`
2. `EvolutionAPIService.send_text_message()`
3. Evolution API envia mensagem

---

## Observações Críticas

1. **Webhook já está ativo** em `/api/whatsapp/webhook/evolution/`
2. **Fluxo conversacional já existe** via `WhatsAppFlowEngine`
3. **Modelos de mensagens já existem** e estão sendo usados
4. **Não há endpoint de console/conversas** ainda
5. **Não há endpoint de sugestões de IA** ainda
6. **Não há multi-tenant por shopper_id** ainda (usa instância única)

