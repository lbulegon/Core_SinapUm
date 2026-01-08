# Resultado do Reinício Limpo - Evolution API

**Data:** 2026-01-05  
**Status:** ⚠️ Parcialmente funcional - Erro `decodeFrame` ainda persiste

## ✅ O que Funcionou

1. **Containers iniciados corretamente**
   - `evolution-api`: Up (health: starting → healthy)
   - `evolution_redis`: Up (healthy)
   - PostgreSQL: Up (externo)

2. **API respondendo**
   - Status: `200 OK`
   - Versão: `2.2.3`
   - Endpoint raiz funcionando

3. **CONFIG_SESSION_PHONE_VERSION aplicada**
   - Valor: `2.2413.51`
   - Confirmado nos logs: `Baileys version env: 2,2413,51`
   - Versão está sendo usada corretamente

4. **Instância criada com sucesso**
   - Instância `test-1767663347` criada
   - Status: `connecting`

## ❌ Problemas que Persistem

1. **QR Code não gera**
   - `count: 0` (QR não disponível)
   - Instância permanece em `connecting`

2. **Erro `decodeFrame` ainda presente**
   - Múltiplos erros: `Connection Failure` e `connection errored`
   - Erro ocorre em: `Object.decodeFrame (/evolution/node_modules/baileys/lib/Utils/noise-handler.js:144:17)`

3. **Versão da API ainda é 2.2.3**
   - Mesmo usando `latest`, a imagem ainda é `v2.2.3`
   - Pode indicar que `latest` aponta para `v2.2.3` no momento

## 🔍 Análise dos Logs

### Logs Relevantes

```
Baileys version env: 2,2413,51  ✅ (CONFIG_SESSION_PHONE_VERSION está sendo usada)
not logged in, attempting registration...  ✅ (tentando conectar)
Error: Connection Failure at decodeFrame  ❌ (erro persiste)
```

### Observações

1. **Versão do WhatsApp Web:**
   - Configurada: `2.2413.51`
   - Verificar se há versão mais recente disponível

2. **Versão da Evolution API:**
   - Atual: `v2.2.3`
   - Pode ter bug conhecido com `decodeFrame`

3. **Erro `decodeFrame`:**
   - Ocorre durante tentativa de conexão com WhatsApp Web
   - Pode ser:
     - Incompatibilidade de versão
     - Problema de rede/firewall
     - Bug na Evolution API 2.2.3

## 🚀 Próximos Passos Recomendados

### 1. Verificar Versão do WhatsApp Web

```bash
./scripts/get_wa_version.sh
# Se versão mudou, atualizar CONFIG_SESSION_PHONE_VERSION
```

### 2. Testar Sem Redis (Isolamento)

```bash
docker compose -f docker-compose.yml -f docker-compose.no-redis.yml up -d
# Criar nova instância e testar QR code
```

### 3. Verificar se Há Versão Mais Recente da Evolution API

```bash
# Verificar tags disponíveis no Docker Hub
docker search atendai/evolution-api

# Ou tentar imagem alternativa
# evoapicloud/evolution-api:homolog (mencionada em issues)
```

### 4. Verificar Logs Detalhados

```bash
docker compose logs evolution-api | grep -E "(qrcode|QR|decodeFrame|error|version)" -i | tail -50
```

### 5. Verificar Conectividade de Rede

```bash
# Testar se container consegue acessar WhatsApp Web
docker exec evolution-api wget -O- https://web.whatsapp.com 2>&1 | head -10
```

## 📊 Status Atual

| Item | Status | Observação |
|------|--------|------------|
| Containers | ✅ OK | Todos iniciados e healthy |
| API Respondendo | ✅ OK | Status 200 |
| CONFIG_SESSION_PHONE_VERSION | ✅ OK | Sendo usada corretamente |
| Instância Criada | ✅ OK | Status: connecting |
| QR Code Gerado | ❌ FALHOU | count: 0 |
| Erro decodeFrame | ❌ PRESENTE | Múltiplos erros |
| Versão API | ⚠️ 2.2.3 | Pode ter bug conhecido |

## 🔧 Comandos Úteis

### Verificar Status Completo

```bash
docker compose ps
curl -s http://localhost:8004/ | python3 -m json.tool
```

### Criar Nova Instância de Teste

```bash
INSTANCE_ID="test-$(date +%s)"
curl -X POST http://localhost:8004/instance/create \
  -H "apikey: GKvy6psn-8HHpBQ4HAHKFOXnwjHR-oSzeGZzCaws0xg" \
  -H "Content-Type: application/json" \
  -d "{\"instanceName\": \"$INSTANCE_ID\", \"qrcode\": true, \"integration\": \"WHATSAPP-BAILEYS\"}"

sleep 15

curl -X GET "http://localhost:8004/instance/connect/$INSTANCE_ID" \
  -H "apikey: GKvy6psn-8HHpBQ4HAHKFOXnwjHR-oSzeGZzCaws0xg"
```

### Monitorar Logs em Tempo Real

```bash
docker compose logs -f evolution-api | grep -E "(qrcode|QR|decodeFrame|error)" -i
```

## 💡 Conclusão

O reinício limpo foi executado com sucesso, mas o erro `decodeFrame` persiste. Isso indica que:

1. ✅ A configuração está correta (`CONFIG_SESSION_PHONE_VERSION` sendo usada)
2. ❌ O problema pode estar na versão da Evolution API (2.2.3 pode ter bug)
3. ❌ Ou na versão do WhatsApp Web (pode ter atualizado)
4. ❌ Ou em problema de rede/firewall

**Recomendação:** Testar sem Redis e verificar se há versão mais recente do WhatsApp Web ou da Evolution API.

---

**Última atualização:** 2026-01-05
