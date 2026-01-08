# Implementação de WebSocket Listener - Evolution API

## Objetivo

Implementar listener de WebSocket para receber eventos de QR code em tempo real da Evolution API, já que o endpoint REST pode não retornar o QR code imediatamente.

## Arquivos Criados

### 1. `app_whatsapp_gateway/clients/websocket_client.py`

Cliente WebSocket para conectar à Evolution API e receber eventos em tempo real.

**Funcionalidades:**
- Conexão WebSocket com Evolution API
- Recebimento de eventos (`qrcode.updated`, `connection.update`, etc.)
- Sistema de handlers para processar eventos
- Suporte para uso síncrono e assíncrono

**Uso:**
```python
from app_whatsapp_gateway.clients.websocket_client import EvolutionWebSocketClient

client = EvolutionWebSocketClient()

# Registrar handler para QR code
@client.on_event('qrcode.updated')
def handle_qrcode(event_data):
    qrcode = event_data.get('data', {}).get('qrcode', {})
    if isinstance(qrcode, dict):
        base64 = qrcode.get('base64')
        if base64:
            print(f"QR code recebido: {base64[:50]}...")

# Conectar e começar a ouvir
await client.connect('instance_id')
```

### 2. `app_whatsapp_gateway/services/websocket_service.py`

Service para gerenciar conexões WebSocket e integrar com o banco de dados.

**Funcionalidades:**
- Gerenciamento de múltiplas conexões WebSocket
- Processamento automático de eventos de QR code
- Atualização automática de instâncias no banco de dados
- Processamento de eventos de conexão

**Uso:**
```python
from app_whatsapp_gateway.services.websocket_service import websocket_service

# Iniciar listener para uma instância
websocket_service.start_listening_for_instance('instance_id')

# Verificar se está ouvindo
if websocket_service.is_listening('instance_id'):
    print("WebSocket ativo")

# Parar listener
websocket_service.stop_listening_for_instance('instance_id')
```

## Integração

O WebSocket service foi integrado ao `InstanceService`:
- Quando uma instância é criada, o WebSocket listener é iniciado automaticamente
- Eventos de QR code são processados e salvos no banco de dados
- Eventos de conexão atualizam o status da instância

## Configuração no Docker Compose

Adicionado ao `docker-compose.yml`:
```yaml
# WebSocket - Habilitado para receber eventos de QR code
WEBSOCKET_ENABLED: true
WEBSOCKET_GLOBAL_EVENTS: true
```

## Dependências

**Pacote necessário:**
```bash
pip install websockets
```

Adicionar ao `requirements.txt`:
```
websockets>=11.0
```

## Eventos Suportados

### 1. `qrcode.updated` / `QRCODE_UPDATED`
Quando o QR code é gerado ou atualizado.

**Formato do evento:**
```json
{
  "event": "qrcode.updated",
  "data": {
    "qrcode": {
      "base64": "data:image/png;base64,...",
      "url": "https://..."
    }
  }
}
```

### 2. `connection.update` / `CONNECTION_UPDATE`
Quando o status de conexão muda.

**Formato do evento:**
```json
{
  "event": "connection.update",
  "data": {
    "state": "open" | "close" | "connecting",
    "phone": {
      "number": "+5511999999999",
      "name": "Nome WhatsApp"
    }
  }
}
```

## Como Funciona

1. **Criação de Instância:**
   - Instância é criada na Evolution API
   - WebSocket listener é iniciado automaticamente
   - Listener fica aguardando eventos

2. **Recebimento de QR Code:**
   - Evolution API gera QR code
   - Evento `qrcode.updated` é enviado via WebSocket
   - Handler processa evento e atualiza banco de dados
   - QR code fica disponível para uso

3. **Atualização de Status:**
   - Quando WhatsApp é conectado, evento `connection.update` é enviado
   - Status da instância é atualizado no banco
   - Instância fica disponível para envio de mensagens

## Vantagens

✅ **Tempo Real**: QR code é recebido assim que é gerado  
✅ **Confiável**: Não depende de polling ou retry  
✅ **Eficiente**: Usa menos recursos que polling constante  
✅ **Automático**: Integrado ao fluxo de criação de instâncias  

## Troubleshooting

### WebSocket não conecta
- Verificar se `WEBSOCKET_ENABLED: true` está configurado
- Verificar se porta WebSocket está aberta
- Verificar logs da Evolution API

### Eventos não são recebidos
- Verificar se `WEBSOCKET_GLOBAL_EVENTS: true` está configurado
- Verificar logs do WebSocket client
- Verificar se instância existe na Evolution API

### QR code não é salvo
- Verificar se handler está registrado corretamente
- Verificar logs de erro
- Verificar se instância existe no banco de dados

## Próximos Passos

1. ✅ Implementação básica completa
2. ⏳ Testar em ambiente de produção
3. ⏳ Adicionar retry automático em caso de desconexão
4. ⏳ Adicionar monitoramento de conexões WebSocket
5. ⏳ Implementar reconexão automática
