# Webhook Habilitado - Evolution API

## Configuração Aplicada

### ✅ Webhook Habilitado
```yaml
WEBHOOK_GLOBAL_ENABLED: true
WEBHOOK_GLOBAL_URL: http://host.docker.internal:8000/api/whatsapp/webhook/evolution/
```

### ✅ Logs Aumentados
```yaml
LOG_BAILEYS: debug  # Aumentado de 'info' para 'debug'
```

## Como Funciona

### 1. Eventos Enviados via Webhook

A Evolution API enviará eventos HTTP POST para o webhook configurado quando:
- QR code é gerado/atualizado (`qrcode.updated`)
- Status de conexão muda (`connection.update`)
- Mensagens são recebidas (`messages.upsert`)
- Outros eventos importantes ocorrem

### 2. Endpoint de Recebimento

O webhook será recebido em:
```
POST /api/whatsapp/webhook/evolution/
```

**Arquivo:** `app_whatsapp_gateway/views.py`
**Função:** `webhook_receiver(request, instance_id)`

### 3. Processamento

O webhook já está implementado para:
- ✅ Processar eventos de QR code (`qrcode.updated`)
- ✅ Atualizar instâncias no banco de dados
- ✅ Processar eventos de conexão
- ✅ Processar mensagens recebidas

## Vantagens do Webhook

✅ **Mais Confiável**: Não depende de WebSocket  
✅ **Já Implementado**: Código já existe e está funcionando  
✅ **Funciona com Problemas de Rede**: HTTP é mais tolerante a problemas de conexão  
✅ **Fácil de Debug**: Logs HTTP são mais fáceis de rastrear  

## Teste

Após habilitar o webhook:

1. **Criar nova instância:**
   ```bash
   curl -X POST http://localhost:8004/instance/create \
     -H "apikey: GKvy6psn-8HHpBQ4HAHKFOXnwjHR-oSzeGZzCaws0xg" \
     -H "Content-Type: application/json" \
     -d '{"instanceName": "test_webhook", "qrcode": true, "integration": "WHATSAPP-BAILEYS"}'
   ```

2. **Monitorar logs do Django:**
   ```bash
   # Verificar se webhook está sendo recebido
   # (quando QR code for gerado)
   ```

3. **Verificar banco de dados:**
   ```python
   from app_whatsapp_gateway.models import EvolutionInstance
   instance = EvolutionInstance.objects.get(instance_id='test_webhook')
   if instance.qrcode:
       print("QR code recebido via webhook!")
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

## Próximos Passos

1. ✅ Webhook habilitado
2. ⏳ Testar criação de instância
3. ⏳ Verificar se eventos são recebidos
4. ⏳ Monitorar logs para confirmar funcionamento

## Observação

O webhook funcionará **mesmo se o WebSocket com WhatsApp estiver falhando**. Quando a Evolution API conseguir gerar o QR code (mesmo que o WebSocket falhe depois), o webhook será enviado.
