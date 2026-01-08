# 📋 Resumo das Correções - Evolution API

## 🎯 Objetivo

Corrigir o stack Docker da Evolution API para:
- ✅ Gerar QR Code corretamente
- ✅ Evitar erro `decodeFrame`
- ✅ Evitar instâncias caindo (connecting → close)
- ✅ Manter configuração estável e observável

## 📦 Arquivos Criados/Modificados

### 1. **docker-compose.yml** ✅ ATUALIZADO
**Mudanças principais:**
- ✅ Removido `CONFIG_SESSION_PHONE_VERSION` (auto-detecção)
- ✅ Adicionado `healthcheck` para ambos serviços
- ✅ `restart: unless-stopped` (melhor prática)
- ✅ Redis com persistência e política de memória
- ✅ `depends_on` com condição de saúde

### 2. **Dockerfile.evolution** ✅ ATUALIZADO
**Mudanças principais:**
- ✅ Atualizado para `atendai/evolution-api:latest`
- ✅ Removida instalação de Chromium (não necessária)
- ✅ Comentários explicativos adicionados

**Nota:** Este Dockerfile pode ser removido se usar imagem diretamente no `docker-compose.yml`.

### 3. **scripts/get_wa_version.sh** ✅ NOVO
Script para obter versão atual do WhatsApp Web.

**Uso:**
```bash
./scripts/get_wa_version.sh
```

### 4. **docker-compose.override.yml.example** ✅ NOVO
Exemplo de override para testar sem Redis (modo DEBUG).

**Uso:**
```bash
cp docker-compose.override.yml.example docker-compose.override.yml
docker compose up -d
```

### 5. **CHECKLIST_VALIDACAO.md** ✅ NOVO
Checklist completo de validação com comandos exatos.

### 6. **CHANGELOG_CORRECOES.md** ✅ NOVO
Changelog detalhado de todas as mudanças.

## 🚀 Como Aplicar

### Passo 1: Fazer Backup (Opcional)
```bash
cd /root/Core_SinapUm/services/evolution_api_service
cp docker-compose.yml docker-compose.yml.backup
```

### Passo 2: Parar Containers
```bash
docker compose down
```

### Passo 3: Reconstruir Imagem
```bash
docker compose build evolution-api
```

### Passo 4: Iniciar Containers
```bash
docker compose up -d
```

### Passo 5: Validar
```bash
# Verificar status
docker compose ps

# Verificar logs
docker compose logs -f evolution-api

# Testar health
curl http://localhost:8004/health
```

## 🔍 Principais Correções Técnicas

### 1. Auto-detecção de Versão do WhatsApp Web
**Antes:** `CONFIG_SESSION_PHONE_VERSION: 2.2413.51` (fixa)  
**Depois:** Removida (auto-detecção pela Evolution API)

**Motivo:** Evita incompatibilidades quando WhatsApp Web atualiza.

### 2. Healthchecks
**Adicionado:**
- Healthcheck para `evolution-api` (verifica endpoint `/health`)
- Healthcheck para `redis` (verifica com `redis-cli ping`)

**Benefício:** Docker sabe quando serviços estão prontos.

### 3. Redis com Persistência
**Adicionado:**
- `--appendonly yes` (persistência)
- `--maxmemory 256mb` (limite de memória)
- `--maxmemory-policy allkeys-lru` (política de eviction)

**Benefício:** Evita perda de dados e controla uso de memória.

### 4. Dependências com Condição
**Antes:** `depends_on: - redis`  
**Depois:** `depends_on: redis: condition: service_healthy`

**Benefício:** Evolution API só inicia quando Redis está realmente pronto.

## 📊 Comparação: Antes vs Depois

| Aspecto | Antes | Depois |
|--------|-------|--------|
| **Versão WhatsApp** | Fixa (2.2413.51) | Auto-detectada |
| **Healthcheck** | ❌ Não | ✅ Sim |
| **Restart Policy** | `always` | `unless-stopped` |
| **Redis Persistência** | ❌ Não | ✅ Sim |
| **Chromium** | Instalado (desnecessário) | Removido |
| **Observabilidade** | Básica | Melhorada |

## ✅ Critérios de Sucesso

Após aplicar as correções, você deve ver:

1. ✅ Containers iniciam sem erros
2. ✅ Health checks passam (`Up (healthy)`)
3. ✅ Instância é criada com sucesso
4. ✅ QR code é gerado (`count > 0`)
5. ✅ Instância permanece em `connecting` (não cai)
6. ✅ Logs não mostram `decodeFrame` recorrente
7. ✅ Após escanear QR, instância muda para `open`

## 🐛 Troubleshooting Rápido

### Container não inicia
```bash
docker compose logs evolution-api
```

### QR Code não gera
```bash
# Verificar logs
docker compose logs evolution-api | grep -i qr

# Verificar instância
curl -X GET "http://localhost:8004/instance/fetchInstances" \
  -H "apikey: GKvy6psn-8HHpBQ4HAHKFOXnwjHR-oSzeGZzCaws0xg"
```

### Erro decodeFrame
```bash
# Verificar versão
docker inspect evolution-api | grep -i version

# Atualizar para latest
# Editar docker-compose.yml e reconstruir
```

## 📚 Documentação Adicional

- **CHECKLIST_VALIDACAO.md** - Validação completa passo a passo
- **CHANGELOG_CORRECOES.md** - Detalhes técnicos das mudanças
- **scripts/get_wa_version.sh** - Script para atualizar versão do WhatsApp

## 🔄 Manutenção Futura

### Atualizar Versão do WhatsApp Web (quando necessário)
```bash
./scripts/get_wa_version.sh
# Seguir instruções do script
```

### Atualizar Evolution API
```bash
# Editar docker-compose.yml
# Alterar tag da imagem (ou usar latest)
docker compose build evolution-api
docker compose up -d
```

---

**Data:** 2025-01-05  
**Versão da Evolution API:** `latest` (atendai/evolution-api:latest)  
**Status:** ✅ Pronto para aplicação
