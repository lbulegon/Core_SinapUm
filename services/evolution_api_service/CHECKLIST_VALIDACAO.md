# Checklist de Validação - Evolution API

## 📋 Pré-requisitos

- [ ] Docker e Docker Compose instalados
- [ ] PostgreSQL rodando em `host.docker.internal:5433`
- [ ] Porta 8004 disponível
- [ ] Porta 6379 disponível (Redis)

## 🔧 Configuração Inicial

### 1. Atualizar Versão do WhatsApp Web (Opcional)

```bash
cd /root/Core_SinapUm/services/evolution_api_service
./scripts/get_wa_version.sh
```

**Nota:** A Evolution API detecta automaticamente a versão. Só configure manualmente se necessário.

### 2. Execução Limpa (Recomendado)

```bash
cd /root/Core_SinapUm/services/evolution_api_service

# Parar containers
docker compose down

# Remover volumes (CUIDADO: apaga instâncias existentes)
# docker compose down -v

# Reconstruir imagem (se usar build)
docker compose build evolution-api

# Iniciar containers
docker compose up -d

# Verificar status
docker compose ps
```

## ✅ Validação Passo a Passo

### 1. Verificar Containers em Execução

```bash
docker compose ps
```

**Esperado:**
- `evolution-api` - Status: `Up (healthy)`
- `evolution_redis` - Status: `Up (healthy)`

### 2. Verificar Logs da Evolution API

```bash
docker compose logs -f evolution-api
```

**Procurar por:**
- ✅ `Server started on port 8080`
- ✅ `Redis connected`
- ✅ `Database connected`
- ❌ **NÃO deve aparecer:** `decodeFrame`, `connection errored` repetidamente

### 3. Verificar Health Check

```bash
curl -s http://localhost:8004/health | jq .
```

**Ou sem jq:**
```bash
curl -s http://localhost:8004/health
```

**Esperado:** Resposta JSON com status `ok` ou similar

### 4. Verificar Endpoint de Instâncias

```bash
curl -X GET http://localhost:8004/instance/fetchInstances \
  -H "apikey: GKvy6psn-8HHpBQ4HAHKFOXnwjHR-oSzeGZzCaws0xg"
```

**Esperado:** Lista de instâncias (pode estar vazia)

### 5. Criar Nova Instância

```bash
INSTANCE_ID="test-$(date +%s)"

curl -X POST http://localhost:8004/instance/create \
  -H "apikey: GKvy6psn-8HHpBQ4HAHKFOXnwjHR-oSzeGZzCaws0xg" \
  -H "Content-Type: application/json" \
  -d "{
    \"instanceName\": \"$INSTANCE_ID\",
    \"qrcode\": true,
    \"integration\": \"WHATSAPP-BAILEYS\"
  }"
```

**Esperado:** JSON com `success: true` e `instance` criada

### 6. Obter QR Code

```bash
curl -X GET "http://localhost:8004/instance/connect/$INSTANCE_ID" \
  -H "apikey: GKvy6psn-8HHpBQ4HAHKFOXnwjHR-oSzeGZzCaws0xg"
```

**Esperado:**
- ✅ `"count": 1` ou maior (não `0`)
- ✅ `"qrcode"` presente no JSON
- ✅ `"base64"` ou `"code"` com dados do QR

**Se retornar `{"count": 0}`:**
- Verificar logs: `docker compose logs evolution-api | grep -i qr`
- Verificar se instância está em status `connecting`
- Aguardar 10-15 segundos e tentar novamente

### 7. Verificar Status da Instância

```bash
curl -X GET "http://localhost:8004/instance/fetchInstances" \
  -H "apikey: GKvy6psn-8HHpBQ4HAHKFOXnwjHR-oSzeGZzCaws0xg" | \
  jq ".[] | select(.instance.instanceName == \"$INSTANCE_ID\")"
```

**Esperado:**
- `status: "connecting"` (antes de escanear)
- `status: "open"` (após escanear QR)

### 8. Verificar Webhook (Opcional)

Se o webhook estiver configurado, verificar se eventos estão chegando:

```bash
# No servidor Django, verificar logs do webhook
# ou verificar endpoint de webhook events
```

### 9. Verificar WebSocket (Opcional)

```bash
# Testar conexão WebSocket (requer ferramenta específica)
# ou verificar logs para eventos WebSocket
docker compose logs evolution-api | grep -i websocket
```

## 🐛 Troubleshooting

### Problema: Container não inicia

```bash
# Verificar logs detalhados
docker compose logs evolution-api

# Verificar se porta está em uso
netstat -tuln | grep 8004
```

### Problema: Redis não conecta

```bash
# Verificar Redis
docker compose logs redis
docker exec evolution_redis redis-cli ping

# Deve retornar: PONG
```

### Problema: QR Code não gera (`count: 0`)

```bash
# 1. Verificar logs detalhados
docker compose logs evolution-api | tail -100

# 2. Verificar se instância existe
curl -X GET "http://localhost:8004/instance/fetchInstances" \
  -H "apikey: GKvy6psn-8HHpBQ4HAHKFOXnwjHR-oSzeGZzCaws0xg"

# 3. Tentar deletar e recriar instância
curl -X DELETE "http://localhost:8004/instance/delete/$INSTANCE_ID" \
  -H "apikey: GKvy6psn-8HHpBQ4HAHKFOXnwjHR-oSzeGZzCaws0xg"

# 4. Recriar instância
# (repetir passo 5)
```

### Problema: Erro `decodeFrame`

```bash
# 1. Verificar versão da Evolution API
docker inspect evolution-api | grep -i version

# 2. Atualizar para versão mais recente
# Editar docker-compose.yml e usar: atendai/evolution-api:latest
# ou: atendai/evolution-api:v2.3.0

# 3. Reconstruir e reiniciar
docker compose down
docker compose build evolution-api
docker compose up -d
```

### Problema: Instância cai (connecting → close)

```bash
# 1. Verificar logs para erros específicos
docker compose logs evolution-api | grep -i error

# 2. Verificar se número não está conectado em outro lugar
# 3. Verificar se QR code foi escaneado corretamente
# 4. Tentar modo DEBUG sem Redis (usar docker-compose.override.yml)
```

## 📊 Critérios de Sucesso

- [x] Containers iniciam sem erros
- [x] Health checks passam
- [x] Instância é criada com sucesso
- [x] QR code é gerado (`count > 0`)
- [x] Instância permanece em `connecting` (não cai para `close`)
- [x] Logs não mostram `decodeFrame` recorrente
- [x] Webhook recebe eventos (se configurado)
- [x] Após escanear QR, instância muda para `open`

## 🔄 Manutenção Contínua

### Atualizar Versão do WhatsApp Web (quando necessário)

```bash
cd /root/Core_SinapUm/services/evolution_api_service
./scripts/get_wa_version.sh

# Se necessário, atualizar docker-compose.yml manualmente
# ou usar o comando one-liner sugerido pelo script
```

### Atualizar Evolution API

```bash
# 1. Verificar versão atual
docker inspect evolution-api | grep -i version

# 2. Atualizar docker-compose.yml com nova tag
# 3. Reconstruir
docker compose build evolution-api
docker compose up -d
```

---

**Última atualização:** 2025-01-05  
**Versão da Evolution API:** v2.3.0 (ou latest)  
**Versão do WhatsApp Web:** Auto-detectada
