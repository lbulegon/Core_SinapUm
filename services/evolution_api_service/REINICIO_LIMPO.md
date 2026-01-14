# 🔄 Reinício Limpo - Evolution API

**Objetivo:** Resetar completamente o ambiente para evitar instâncias zumbi e aplicar todas as correções.

## 📋 Passo a Passo

### 1. Parar Todos os Containers

```bash
cd /root/Core_SinapUm/services/evolution_api_service
docker compose down
```

### 2. (Opcional) Remover Volumes de Sessão

**⚠️ ATENÇÃO:** Isso apaga todas as instâncias existentes. Use apenas se quiser começar do zero.

```bash
# Listar volumes
docker volume ls | grep evolution

# Remover volumes (CUIDADO: apaga instâncias)
docker volume rm evolution_api_service_evolution_instances
docker volume rm evolution_api_service_evolution_store
docker volume rm evolution_api_service_evolution_redis_data
```

**OU** se preferir manter os dados:

```bash
# Apenas limpar instâncias antigas via API (recomendado)
# Isso será feito após subir o stack
```

### 3. Atualizar Versão do WhatsApp Web (se necessário)

```bash
# Verificar versão atual
./scripts/get_wa_version.sh

# Se a versão mudou, atualizar docker-compose.yml manualmente
# ou usar o comando one-liner sugerido pelo script
```

### 4. Reconstruir Imagem

```bash
# Reconstruir com nova base (v2.3.6)
docker compose build --no-cache evolution-api
```

### 5. Iniciar Containers

```bash
docker compose up -d
```

### 5.1 (Opcional) Habilitar Debug do Baileys (QR/Handshake)

Use o override de debug para aumentar a verbosidade sem mexer no compose principal:

```bash
docker compose -f docker-compose.yml -f docker-compose.debug.yml up -d
docker compose logs -f evolution-api
```

### 6. Verificar Status

```bash
# Verificar containers
docker compose ps

# Verificar logs
docker compose logs -f evolution-api
```

### 7. Limpar Instâncias Antigas (via API)

```bash
# Listar todas as instâncias
curl -X GET http://localhost:8004/instance/fetchInstances \
  -H "apikey: GKvy6psn-8HHpBQ4HAHKFOXnwjHR-oSzeGZzCaws0xg" | \
  python3 -c "import sys, json; insts=json.load(sys.stdin); [print(f\"{i.get('instance', {}).get('instanceName', 'N/A')} - {i.get('instance', {}).get('status', 'N/A')}\") for i in insts]"

# Deletar instâncias em status 'close' ou problemáticas
# (ajustar INSTANCE_NAME conforme necessário)
curl -X DELETE "http://localhost:8004/instance/delete/INSTANCE_NAME" \
  -H "apikey: GKvy6psn-8HHpBQ4HAHKFOXnwjHR-oSzeGZzCaws0xg"
```

### 8. Criar Instância Nova de Teste

```bash
INSTANCE_ID="test-$(date +%s)"
echo "Criando instância: $INSTANCE_ID"

curl -X POST http://localhost:8004/instance/create \
  -H "apikey: GKvy6psn-8HHpBQ4HAHKFOXnwjHR-oSzeGZzCaws0xg" \
  -H "Content-Type: application/json" \
  -d "{
    \"instanceName\": \"$INSTANCE_ID\",
    \"qrcode\": true,
    \"integration\": \"WHATSAPP-BAILEYS\"
  }"

# Aguardar 10 segundos para inicialização
sleep 10

# Verificar QR code
curl -X GET "http://localhost:8004/instance/connect/$INSTANCE_ID" \
  -H "apikey: GKvy6psn-8HHpBQ4HAHKFOXnwjHR-oSzeGZzCaws0xg" | \
  python3 -c "import sys, json; d=json.load(sys.stdin); qr=d.get('qrcode', {}); print(f\"QR Count: {qr.get('count', 0)}\"); print(f\"Status: {d.get('instance', {}).get('status', 'N/A')}\")"
```

## 🧰 Script de Diagnóstico (automático)

Cria uma instância e faz polling do `/instance/connect`, além de filtrar os logs por erros comuns:

```bash
cd /root/Core_SinapUm/services/evolution_api_service
bash scripts/diagnose_qr.sh
```

## 🧪 Teste A/B: Com e Sem Redis

### Teste COM Redis (padrão)

```bash
docker compose up -d
# Seguir passos acima
```

### Teste SEM Redis (isolamento)

```bash
# Usar override sem Redis
docker compose -f docker-compose.yml -f docker-compose.no-redis.yml up -d

# Testar criação de instância e QR code
# Se funcionar sem Redis, o problema pode estar na configuração do Redis
```

## ✅ Checklist de Validação

Após reinício limpo, verificar:

- [ ] Containers iniciam sem erros
- [ ] Health checks passam (`Up (healthy)`)
- [ ] Versão da API é v2.3.6 (ou mais recente)
- [ ] `CONFIG_SESSION_PHONE_VERSION` está atualizada
- [ ] Instância é criada com sucesso
- [ ] QR code é gerado (`count > 0`)
- [ ] Instância permanece em `connecting` (não cai para `close`)
- [ ] Logs não mostram `decodeFrame` recorrente
- [ ] Após escanear QR, instância muda para `open`

## 🔍 Troubleshooting

### Se QR code ainda não gerar:

1. **Verificar versão do WhatsApp Web:**
   ```bash
   ./scripts/get_wa_version.sh
   # Atualizar CONFIG_SESSION_PHONE_VERSION se necessário
   ```

2. **Verificar logs detalhados:**
   ```bash
   docker compose logs evolution-api | grep -E "(qrcode|QR|decodeFrame|error)" -i | tail -30
   ```

3. **Testar sem Redis:**
   ```bash
   docker compose -f docker-compose.yml -f docker-compose.no-redis.yml up -d
   ```

4. **Verificar se versão da API está correta:**
   ```bash
   docker inspect evolution-api | grep -i version
   curl -s http://localhost:8004/ | python3 -c "import sys, json; print(json.load(sys.stdin).get('version'))"
   ```

---

**Última atualização:** 2026-01-05
