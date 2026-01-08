# Soluções para Erro de WebSocket - Evolution API

## Problema Identificado

A Evolution API está apresentando erros de conexão WebSocket:
```
Error: Connection Failure
at WebSocketClient.<anonymous>
msg: "connection errored"
```

Isso impede a geração do QR code, mesmo com conectividade básica funcionando (ping e DNS OK).

## Soluções Recomendadas

### 1. Remover ou Atualizar CONFIG_SESSION_PHONE_VERSION ⚠️

**Problema:** A versão do WhatsApp pode estar desatualizada ou incompatível.

**Solução A - Remover a variável:**
```yaml
# Comentar ou remover esta linha do docker-compose.yml:
# CONFIG_SESSION_PHONE_VERSION: 2.3000.1025205472
```

**Solução B - Atualizar para versão mais recente:**
1. Acessar https://web.whatsapp.com
2. Verificar versão atual nas configurações
3. Atualizar `CONFIG_SESSION_PHONE_VERSION` no docker-compose.yml

### 2. Desativar IPv6 (se aplicável)

Se o servidor tiver problemas com IPv6, pode forçar apenas IPv4:

```yaml
# Adicionar ao docker-compose.yml:
sysctls:
  - net.ipv6.conf.all.disable_ipv6=1
  - net.ipv6.conf.default.disable_ipv6=1
```

### 3. Verificar Configurações de WebSocket

A Evolution API usa WebSocket para comunicação. Verificar se está habilitado:

```yaml
# Adicionar se não existir:
WEBSOCKET_ENABLED: true
```

### 4. Verificar Firewall/Proxy

O WebSocket pode estar sendo bloqueado. Verificar:
- Firewall do servidor
- Proxy reverso (se houver)
- Regras de iptables

### 5. Atualizar Imagem Docker

Algumas versões têm bugs conhecidos. Tentar atualizar:

```bash
cd /root/Core_SinapUm/services/evolution_api_service
docker compose pull
docker compose up -d
```

## Teste Recomendado

1. **Primeiro, tentar remover CONFIG_SESSION_PHONE_VERSION:**
   ```bash
   # Editar docker-compose.yml e comentar a linha
   # CONFIG_SESSION_PHONE_VERSION: 2.3000.1025205472
   
   # Reiniciar
   docker compose restart evolution-api
   ```

2. **Se não funcionar, tentar atualizar a versão:**
   - Verificar versão atual do WhatsApp Web
   - Atualizar no docker-compose.yml
   - Reiniciar

3. **Verificar logs após mudanças:**
   ```bash
   docker compose logs -f evolution-api | grep -i websocket
   ```

## Status Atual

- ✅ Conectividade básica: OK (ping, DNS funcionando)
- ✅ DNS resolvendo: OK (web.whatsapp.com resolve corretamente)
- ❌ WebSocket: Falhando (Connection Failure)
- ❌ QR Code: Não sendo gerado (devido ao erro de WebSocket)

## Próximos Passos

1. Testar remover `CONFIG_SESSION_PHONE_VERSION`
2. Se não funcionar, atualizar para versão mais recente
3. Verificar se há atualizações da imagem Docker
4. Considerar usar WebSocket events para receber QR code (se disponível na API)
