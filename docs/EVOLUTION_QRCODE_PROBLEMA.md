# Problema: QR Code não está sendo gerado - Evolution API

## Diagnóstico

### Problema Identificado
O endpoint `/instance/connect/{instance_name}` está retornando apenas `{"count": 0}` ao invés de retornar o QR code em base64.

### Testes Realizados

1. **Endpoint `/instance/connect/{instance_name}` (GET)**
   - Retorna: `{"count": 0}`
   - Não retorna o QR code em base64

2. **Endpoint `/instance/qrcode/{instance_name}` (GET)**
   - Retorna: 404 Not Found
   - Endpoint não existe

3. **Criação de instância `/instance/create` (POST)**
   - Resposta inclui: `"qrcode": {"count": 0}`
   - QR code não vem na resposta de criação

4. **Logs do Container**
   - Há erros de conexão WebSocket com WhatsApp
   - "connection errored" aparece nos logs
   - Erros de DNS: "getaddrinfo EAI_AGAIN web.whatsapp.com"

## Possíveis Causas

### 1. QR Code via WebSocket (Mais Provável)
Na Evolution API v2.1.1, o QR code geralmente é obtido através de WebSocket, não através de REST API. O endpoint `/instance/connect/{instance_name}` via REST pode não retornar o QR code diretamente.

### 2. Problemas de Conexão
Os logs mostram erros de conexão WebSocket com o WhatsApp:
- `Error: WebSocket Error (getaddrinfo EAI_AGAIN web.whatsapp.com)`
- `Error: Connection Failure`

Isso pode impedir a geração do QR code.

### 3. Endpoint Incorreto
O endpoint REST pode não ser o correto para obter QR code. Na Evolution API, o QR code pode vir através de:
- WebSocket (recomendado)
- Endpoint REST específico (que pode não estar funcionando)
- Na resposta de criação (mas pode demorar)

## Soluções Possíveis

### Solução 1: Implementar WebSocket (Recomendado)
Conectar via WebSocket para receber eventos do QR code:
```
ws://127.0.0.1:8004/instance/connect/{instance_name}
```

### Solução 2: Usar endpoint diferente
Tentar outros endpoints possíveis:
- Verificar documentação da Evolution API
- Testar endpoints alternativos

### Solução 3: Verificar conectividade
Resolver problemas de conexão com WhatsApp:
- Verificar firewall/rede
- Verificar DNS
- Verificar se o servidor tem acesso à internet

## Próximos Passos

1. Verificar documentação oficial da Evolution API v2.1.1
2. Testar conexão WebSocket
3. Verificar problemas de rede/conectividade
4. Considerar implementar WebSocket no Django

## Referências

- Evolution API Documentation: https://doc.evolution-api.com
- Versão: v2.1.1
- API URL: http://127.0.0.1:8004

