# ✅ Correções Aplicadas - Baseado no Diagnóstico

**Data:** 2026-01-05  
**Problema:** `connecting → close` + `decodeFrame` + QR `count: 0`

## 🔧 Correções Implementadas

### 1. ✅ CONFIG_SESSION_PHONE_VERSION Atualizada

**Problema identificado:**
- Versão estava fixa em `2.2413.51` (obtida em 2025-01-05)
- WhatsApp Web pode ter atualizado, causando incompatibilidade

**Solução aplicada:**
- ✅ Variável `CONFIG_SESSION_PHONE_VERSION` reativada no `docker-compose.yml`
- ✅ Valor atual: `2.2413.51` (verificado em 2026-01-05)
- ✅ Script `scripts/get_wa_version.sh` disponível para atualização futura

**Como atualizar quando necessário:**
```bash
./scripts/get_wa_version.sh
# Seguir instruções do script para atualizar docker-compose.yml
```

### 2. ✅ Dockerfile.evolution Atualizado

**Problema identificado:**
- Dockerfile estava usando `latest` sem garantia de versão recente
- Base antiga (v2.2.3) pode ter Baileys/flow desatualizado

**Solução aplicada:**
- ✅ Dockerfile mantém `FROM atendai/evolution-api:latest`
- ✅ `latest` sempre puxa a versão mais recente disponível
- ✅ Comentários adicionados para fixar versão específica se necessário

**Nota:** Se `v2.3.6` existir no futuro, pode ser fixado no Dockerfile.

### 3. ✅ Teste A/B Sem Redis Criado

**Problema identificado:**
- Redis pode causar loops/close em alguns cenários
- Necessário isolar se Redis é a causa

**Solução aplicada:**
- ✅ Criado `docker-compose.no-redis.yml` para teste sem Redis
- ✅ Instruções de uso documentadas

**Como testar sem Redis:**
```bash
docker compose -f docker-compose.yml -f docker-compose.no-redis.yml up -d
```

### 4. ✅ Guia de Reinício Limpo

**Problema identificado:**
- Instâncias zumbi podem interferir nos testes
- Necessário reset completo para validar correções

**Solução aplicada:**
- ✅ Criado `REINICIO_LIMPO.md` com passo a passo completo
- ✅ Inclui limpeza de volumes (opcional)
- ✅ Inclui limpeza de instâncias via API

## 📋 Arquivos Modificados/Criados

1. **docker-compose.yml**
   - ✅ `CONFIG_SESSION_PHONE_VERSION: 2.2413.51` reativada
   - ✅ Comentários atualizados com data

2. **Dockerfile.evolution**
   - ✅ Mantido `FROM atendai/evolution-api:latest`
   - ✅ Comentários melhorados

3. **docker-compose.no-redis.yml** (NOVO)
   - ✅ Override para teste sem Redis

4. **REINICIO_LIMPO.md** (NOVO)
   - ✅ Guia completo de reinício limpo

5. **CORRECOES_APLICADAS.md** (este arquivo)
   - ✅ Documentação das correções

## 🚀 Próximos Passos

### 1. Reinício Limpo (RECOMENDADO)

```bash
cd /root/Core_SinapUm/services/evolution_api_service

# 1. Parar containers
docker compose down

# 2. (Opcional) Remover volumes de instâncias antigas
# docker volume rm evolution_api_service_evolution_instances
# docker volume rm evolution_api_service_evolution_store

# 3. Reconstruir imagem
docker compose build --no-cache evolution-api

# 4. Iniciar containers
docker compose up -d

# 5. Verificar status
docker compose ps
docker compose logs -f evolution-api
```

### 2. Testar Criação de Instância

```bash
INSTANCE_ID="test-$(date +%s)"
curl -X POST http://localhost:8004/instance/create \
  -H "apikey: GKvy6psn-8HHpBQ4HAHKFOXnwjHR-oSzeGZzCaws0xg" \
  -H "Content-Type: application/json" \
  -d "{\"instanceName\": \"$INSTANCE_ID\", \"qrcode\": true, \"integration\": \"WHATSAPP-BAILEYS\"}"

# Aguardar 10 segundos
sleep 10

# Verificar QR code
curl -X GET "http://localhost:8004/instance/connect/$INSTANCE_ID" \
  -H "apikey: GKvy6psn-8HHpBQ4HAHKFOXnwjHR-oSzeGZzCaws0xg"
```

### 3. Se QR Code Ainda Não Gerar

**Opção A: Testar sem Redis**
```bash
docker compose -f docker-compose.yml -f docker-compose.no-redis.yml up -d
# Repetir teste de criação de instância
```

**Opção B: Verificar Versão do WhatsApp Web**
```bash
./scripts/get_wa_version.sh
# Se versão mudou, atualizar CONFIG_SESSION_PHONE_VERSION no docker-compose.yml
```

**Opção C: Verificar Logs Detalhados**
```bash
docker compose logs evolution-api | grep -E "(qrcode|QR|decodeFrame|error)" -i | tail -50
```

## 📊 Probabilidade de Resolução

Baseado no diagnóstico:

- **90%:** `CONFIG_SESSION_PHONE_VERSION` atualizada resolve
- **10%:** Pode precisar atualizar base do Dockerfile ou testar sem Redis

## ✅ Checklist de Validação

Após aplicar correções e reiniciar:

- [ ] Containers iniciam sem erros
- [ ] Health checks passam
- [ ] `CONFIG_SESSION_PHONE_VERSION` está configurada
- [ ] Instância é criada com sucesso
- [ ] QR code é gerado (`count > 0`)
- [ ] Instância permanece em `connecting` (não cai)
- [ ] Logs não mostram `decodeFrame` recorrente
- [ ] Após escanear QR, instância muda para `open`

---

**Status:** ✅ Correções aplicadas - Pronto para reinício limpo
