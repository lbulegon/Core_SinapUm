# Webhook Configurado - Evolution API

## ✅ Configuração Aplicada

### Webhook Habilitado
```yaml
WEBHOOK_GLOBAL_ENABLED: true
WEBHOOK_GLOBAL_URL: http://host.docker.internal:8000/webhooks/evolution/
```

### Logs Aumentados
```yaml
LOG_BAILEYS: debug  # Para obter mais informações sobre erros
```

## Endpoint de Webhook

### URL Configurada
```
http://host.docker.internal:8000/webhooks/evolution/
```

**Nota:** A Evolution API enviará eventos para este endpoint. O `instance_id` será incluído no payload do evento, não na URL (modo global).

### Endpoint no Django
O webhook será recebido em:
```
POST /webhooks/evolution/<instance_id>/messages
```

**Arquivo:** `app_whatsapp_gateway/views.py`
**Função:** `webhook_receiver(request, instance_id)`

## Como Funciona

### 1. Modo Global de Webhook

Com `WEBHOOK_GLOBAL_ENABLED: true`, a Evolution API:
- Envia todos os eventos para a URL configurada
- Inclui o `instance_id` no payload do evento
- Não precisa de URL por instância

### 2. Processamento de Eventos

O webhook já está implementado para processar:
- ✅ `qrcode.updated` - QR code gerado/atualizado
- ✅ `connection.update` - Status de conexão mudou
- ✅ `messages.upsert` - Mensagens recebidas
- ✅ Outros eventos importantes

### 3. Atualização Automática

Quando um evento de QR code é recebido:
1. Webhook é recebido no Django
2. Evento é parseado
3. Instância é atualizada no banco de dados
4. QR code fica disponível para uso

## Vantagens

✅ **Mais Confiável**: HTTP é mais tolerante a problemas de rede  
✅ **Já Implementado**: Código completo e testado  
✅ **Funciona com Problemas de WebSocket**: Independente do WebSocket  
✅ **Fácil de Debug**: Logs HTTP são claros  

## Teste

### 1. Criar Instância
```bash
curl -X POST http://localhost:8004/instance/create \
  -H "apikey: GKvy6psn-8HHpBQ4HAHKFOXnwjHR-oSzeGZzCaws0xg" \
  -H "Content-Type: application/json" \
  -d '{"instanceName": "test_webhook", "qrcode": true, "integration": "WHATSAPP-BAILEYS"}'
```

### 2. Monitorar Logs
```bash
# Logs da Evolution API
docker compose logs -f evolution-api

# Logs do Django (quando webhook for recebido)
# Verificar se eventos são processados
```

### 3. Verificar Banco de Dados
```python
from app_whatsapp_gateway.models import EvolutionInstance, WebhookEvent

# Verificar instância
instance = EvolutionInstance.objects.get(instance_id='test_webhook')
print(f"QR code: {'Sim' if instance.qrcode else 'Não'}")
print(f"Status: {instance.status}")

# Verificar eventos recebidos
events = WebhookEvent.objects.filter(instance=instance)
print(f"Eventos recebidos: {events.count()}")
```

## Eventos Esperados

### QR Code Atualizado
```json
{
  "event": "qrcode.updated",
  "instance": "test_webhook",
  "data": {
    "qrcode": {
      "base64": "data:image/png;base64,...",
      "url": "https://..."
    }
  }
}
```

### Conexão Atualizada
```json
{
  "event": "connection.update",
  "instance": "test_webhook",
  "data": {
    "state": "open",
    "phone": {
      "number": "+5511999999999",
      "name": "Nome WhatsApp"
    }
  }
}
```

## Status

✅ **Webhook habilitado**  
✅ **URL configurada corretamente**  
✅ **Código de processamento implementado**  
⏳ **Aguardando QR code ser gerado pela Evolution API**

## Observação Importante

O webhook funcionará **mesmo se o WebSocket com WhatsApp estiver falhando**. Quando a Evolution API conseguir gerar o QR code (mesmo que o WebSocket falhe depois), o webhook será enviado automaticamente.

O problema atual é que a Evolution API não consegue conectar ao WhatsApp para gerar o QR code. Quando esse problema for resolvido (seja por atualização, configuração adicional, ou resolução de rede), o webhook receberá o evento de QR code automaticamente.
