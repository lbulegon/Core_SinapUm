# 🎯 Entregáveis Finais - Correção Evolution API

## 📋 Resumo Executivo

Todas as correções foram aplicadas para resolver:
- ❌ Erro `decodeFrame`
- ❌ QR Code não gerando (`count: 0`)
- ❌ Instâncias caindo (connecting → close)

**Status:** ✅ Pronto para aplicação

---

## 📦 Arquivos Prontos para Copiar/Colar

### 1. docker-compose.yml

```yaml
services:
  evolution-api:
    # Opção 1: Usar build customizado (se necessário manter Dockerfile)
    build:
      context: .
      dockerfile: Dockerfile.evolution
    # Opção 2: Usar imagem diretamente (RECOMENDADO - mais simples)
    # Descomente a linha abaixo e comente o bloco 'build:' acima para usar imagem direta:
    # image: atendai/evolution-api:latest
    container_name: evolution-api
    restart: unless-stopped
    ports:
      - "8004:8080"
    environment:
      # Configurações básicas
      SERVER_URL: http://69.169.102.84:8004
      PORT: 8080
      
      # Autenticação
      AUTHENTICATION_API_KEY: GKvy6psn-8HHpBQ4HAHKFOXnwjHR-oSzeGZzCaws0xg
      
      # Database - PostgreSQL (usando container existente via host)
      DATABASE_ENABLED: true
      DATABASE_PROVIDER: postgresql
      DATABASE_CONNECTION_URI: postgresql://evolution:I4FD1_hihwvGc3BpZ0nEd7xnengVrnRh@host.docker.internal:5433/evolution
      
      # Redis (serviço local no mesmo docker-compose)
      CACHE_REDIS_ENABLED: true
      CACHE_REDIS_URI: redis://redis:6379/0
      CACHE_REDIS_PREFIX_KEY: evolution
      CACHE_REDIS_SAVE_INSTANCES: false
      CACHE_LOCAL_ENABLED: false
      
      # Configurações de instância
      CONFIG_SESSION_PHONE_CLIENT: Chrome
      CONFIG_SESSION_PHONE_NAME: Evolution API
      # IMPORTANTE: Removido CONFIG_SESSION_PHONE_VERSION para auto-detecção
      # A Evolution API detecta automaticamente a versão correta do WhatsApp Web
      # Se precisar forçar uma versão específica, descomente e atualize:
      # CONFIG_SESSION_PHONE_VERSION: 2.2413.51
      
      # QR Code
      QRCODE_LIMIT: 30
      QRCODE_COLOR: '#198754'
      
      # Webhook - Habilitado para receber eventos de QR code
      WEBHOOK_GLOBAL_ENABLED: true
      WEBHOOK_GLOBAL_URL: http://host.docker.internal:8000/api/whatsapp/webhook/evolution/
      
      # WebSocket - Habilitado para receber eventos de QR code
      WEBSOCKET_ENABLED: true
      WEBSOCKET_GLOBAL_EVENTS: true
      
      # Logs (nível apropriado para produção)
      LOG_LEVEL: INFO
      LOG_COLOR: true
      LOG_BAILEYS: info
      # Para debug detalhado, altere LOG_BAILEYS para: debug
      
    volumes:
      - evolution_instances:/evolution/instances
      - evolution_store:/evolution/store
    networks:
      - evolution-network
    depends_on:
      redis:
        condition: service_healthy
    extra_hosts:
      - "host.docker.internal:host-gateway"
    healthcheck:
      test: ["CMD", "wget", "--no-verbose", "--tries=1", "--spider", "http://localhost:8080/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s

  redis:
    image: redis:7-alpine
    container_name: evolution_redis
    restart: unless-stopped
    ports:
      - "6379:6379"
    volumes:
      - evolution_redis_data:/data
    networks:
      - evolution-network
    command: redis-server --appendonly yes --maxmemory 256mb --maxmemory-policy allkeys-lru
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 3s
      retries: 3
      start_period: 10s

volumes:
  evolution_instances:
  evolution_store:
  evolution_redis_data:

networks:
  evolution-network:
    driver: bridge
```

### 2. Dockerfile.evolution

```dockerfile
# Dockerfile customizado para Evolution API
# NOTA: Chromium NÃO é necessário - a imagem oficial já inclui o necessário
# Este Dockerfile mantém apenas para compatibilidade, mas pode ser removido
# se usar diretamente: image: atendai/evolution-api:latest

# Usando versão latest (atualizada automaticamente)
FROM atendai/evolution-api:latest

# Verificar se a imagem base está funcionando
RUN node --version && npm --version

# NOTA: Chromium não é necessário - Baileys não requer Chromium para QR code
# A geração de QR code é feita via biblioteca JavaScript, não via browser
```

### 3. scripts/get_wa_version.sh

```bash
#!/bin/bash
# Script para obter a versão atual do WhatsApp Web
# Uso: ./scripts/get_wa_version.sh
#      ou: bash scripts/get_wa_version.sh

set -e

WA_CHECK_URL="https://web.whatsapp.com/check-update?version=0&platform=web"

echo "🔍 Consultando versão atual do WhatsApp Web..."
echo ""

# Faz a requisição e extrai a versão
RESPONSE=$(curl -s "$WA_CHECK_URL" || echo "")

if [ -z "$RESPONSE" ]; then
    echo "❌ Erro: Não foi possível conectar ao endpoint do WhatsApp Web"
    echo "   URL: $WA_CHECK_URL"
    exit 1
fi

# Extrai a versão usando jq (se disponível) ou grep/sed
if command -v jq &> /dev/null; then
    VERSION=$(echo "$RESPONSE" | jq -r '.currentVersion // empty')
else
    VERSION=$(echo "$RESPONSE" | grep -o '"currentVersion":"[^"]*"' | cut -d'"' -f4)
fi

if [ -z "$VERSION" ]; then
    echo "❌ Erro: Não foi possível extrair a versão da resposta"
    echo "   Resposta recebida: $RESPONSE"
    exit 1
fi

echo "✅ Versão atual do WhatsApp Web: $VERSION"
echo ""
echo "📋 Para atualizar no docker-compose.yml, altere:"
echo "   CONFIG_SESSION_PHONE_VERSION: $VERSION"
echo ""
echo "💡 Comando one-liner para atualizar:"
echo "   sed -i 's/CONFIG_SESSION_PHONE_VERSION:.*/CONFIG_SESSION_PHONE_VERSION: $VERSION/' docker-compose.yml"
echo ""

# Retorna a versão para uso em scripts
echo "$VERSION"
```

**Permissão:**
```bash
chmod +x scripts/get_wa_version.sh
```

### 4. docker-compose.override.yml.example

```yaml
# docker-compose.override.yml.example
# 
# INSTRUÇÕES:
# 1. Copie este arquivo para docker-compose.override.yml
# 2. Use para testar sem Redis (modo DEBUG)
# 3. Execute: docker compose -f docker-compose.yml -f docker-compose.override.yml up -d
#
# Este arquivo desabilita Redis e usa cache local para testes de isolamento

services:
  evolution-api:
    environment:
      # Desabilita Redis e usa cache local
      CACHE_REDIS_ENABLED: false
      CACHE_LOCAL_ENABLED: true
      # Aumenta logs para debug
      LOG_LEVEL: DEBUG
      LOG_BAILEYS: debug
    # Remove dependência do Redis
    depends_on: []

  # Comenta o serviço Redis (não será iniciado)
  # redis:
  #   profiles:
  #     - disabled
```

---

## 🚀 Comandos de Aplicação

### Execução Limpa (Recomendado)

```bash
cd /root/Core_SinapUm/services/evolution_api_service

# 1. Parar containers
docker compose down

# 2. Reconstruir imagem (se usar build)
docker compose build evolution-api

# 3. Iniciar containers
docker compose up -d

# 4. Verificar status
docker compose ps

# 5. Verificar logs
docker compose logs -f evolution-api
```

### Validação Rápida

```bash
# Health check
curl http://localhost:8004/health

# Listar instâncias
curl -X GET http://localhost:8004/instance/fetchInstances \
  -H "apikey: GKvy6psn-8HHpBQ4HAHKFOXnwjHR-oSzeGZzCaws0xg"

# Criar instância de teste
INSTANCE_ID="test-$(date +%s)"
curl -X POST http://localhost:8004/instance/create \
  -H "apikey: GKvy6psn-8HHpBQ4HAHKFOXnwjHR-oSzeGZzCaws0xg" \
  -H "Content-Type: application/json" \
  -d "{
    \"instanceName\": \"$INSTANCE_ID\",
    \"qrcode\": true,
    \"integration\": \"WHATSAPP-BAILEYS\"
  }"

# Obter QR code
curl -X GET "http://localhost:8004/instance/connect/$INSTANCE_ID" \
  -H "apikey: GKvy6psn-8HHpBQ4HAHKFOXnwjHR-oSzeGZzCaws0xg"
```

---

## 📊 Mudanças Principais

### ✅ O que foi corrigido:

1. **Auto-detecção de versão do WhatsApp Web**
   - Removido `CONFIG_SESSION_PHONE_VERSION` fixo
   - Evolution API detecta automaticamente

2. **Healthchecks adicionados**
   - Evolution API: verifica endpoint `/health`
   - Redis: verifica com `redis-cli ping`

3. **Redis com persistência**
   - `--appendonly yes`
   - Política de memória configurada

4. **Dependências com condição**
   - Evolution API só inicia quando Redis está healthy

5. **Chromium removido**
   - Não é necessário para QR code
   - Baileys usa bibliotecas JavaScript

6. **Restart policy melhorada**
   - `unless-stopped` em vez de `always`

### ❌ O que foi removido:

- `CONFIG_SESSION_PHONE_VERSION` fixa
- Instalação de Chromium no Dockerfile
- `restart: always` (substituído por `unless-stopped`)

---

## ✅ Critérios de Sucesso

Após aplicar, você deve ver:

- [x] Containers iniciam sem erros
- [x] Health checks passam (`Up (healthy)`)
- [x] Instância é criada com sucesso
- [x] QR code é gerado (`count > 0`)
- [x] Instância permanece em `connecting` (não cai)
- [x] Logs não mostram `decodeFrame` recorrente
- [x] Após escanear QR, instância muda para `open`

---

## 📚 Documentação Adicional

Todos os arquivos foram criados em:
- `CHECKLIST_VALIDACAO.md` - Validação completa
- `CHANGELOG_CORRECOES.md` - Detalhes técnicos
- `README_CORRECOES.md` - Resumo executivo

---

**Status:** ✅ Pronto para aplicação  
**Data:** 2025-01-05  
**Versão:** Evolution API `latest` (atendai/evolution-api:latest)
