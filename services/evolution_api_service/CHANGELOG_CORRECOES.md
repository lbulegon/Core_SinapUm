# Changelog - Correções Evolution API

## 2025-01-05 - Correção decodeFrame e QR Code

### 🔧 Mudanças Aplicadas

#### 1. **Dockerfile.evolution**
- ✅ Atualizado para usar `atendai/evolution-api:v2.3.0` (ou `latest`)
- ✅ Removida instalação de Chromium (não é necessária)
- ✅ Adicionado comentário explicando que Chromium não é necessário

**Motivo:** Chromium não é necessário para geração de QR code. Baileys usa bibliotecas JavaScript.

#### 2. **docker-compose.yml**
- ✅ Adicionado `healthcheck` para `evolution-api` e `redis`
- ✅ Alterado `restart: always` para `restart: unless-stopped` (melhor prática)
- ✅ **REMOVIDO** `CONFIG_SESSION_PHONE_VERSION` (auto-detecção)
- ✅ Adicionado `depends_on` com `condition: service_healthy` para Redis
- ✅ Alterado `LOG_BAILEYS` de `debug` para `info` (produção)
- ✅ Redis atualizado para `redis:7-alpine` (mais leve)
- ✅ Adicionado comando Redis com persistência e política de memória

**Motivo:**
- Auto-detecção de versão evita incompatibilidades
- Healthchecks garantem que serviços estão prontos
- Redis com persistência evita perda de dados

#### 3. **Scripts**
- ✅ Criado `scripts/get_wa_version.sh` para obter versão do WhatsApp Web
- ✅ Script inclui comando one-liner para atualização automática

**Motivo:** Facilita atualização manual quando necessário.

#### 4. **Documentação**
- ✅ Criado `docker-compose.override.yml.example` para modo DEBUG sem Redis
- ✅ Criado `CHECKLIST_VALIDACAO.md` com validação completa
- ✅ Criado `CHANGELOG_CORRECOES.md` (este arquivo)

### 📝 Variáveis de Ambiente Alteradas

| Variável | Antes | Depois | Motivo |
|----------|-------|--------|--------|
| `CONFIG_SESSION_PHONE_VERSION` | `2.2413.51` | **Removida** | Auto-detecção |
| `LOG_BAILEYS` | `debug` | `info` | Produção |
| `restart` | `always` | `unless-stopped` | Melhor prática |

### 🆕 Adições

- Healthcheck para `evolution-api`
- Healthcheck para `redis`
- `depends_on` com condição de saúde
- Script de obtenção de versão do WhatsApp Web
- Documentação de validação
- Exemplo de override para modo DEBUG

### 🗑️ Removido

- Instalação de Chromium no Dockerfile (não necessário)
- `CONFIG_SESSION_PHONE_VERSION` fixa (usa auto-detecção)

### ⚠️ Breaking Changes

**Nenhum** - As mudanças são compatíveis com a configuração anterior.

### 🔄 Migração

Para aplicar as correções:

```bash
cd /root/Core_SinapUm/services/evolution_api_service

# 1. Fazer backup (opcional)
cp docker-compose.yml docker-compose.yml.backup

# 2. Aplicar novos arquivos (já aplicados)

# 3. Reconstruir e reiniciar
docker compose down
docker compose build evolution-api
docker compose up -d

# 4. Validar
./scripts/get_wa_version.sh
docker compose ps
docker compose logs -f evolution-api
```

### 📚 Referências

- [Evolution API v2 Documentation](https://doc.evolution-api.com/v2/)
- [Baileys Documentation](https://github.com/WhiskeySockets/Baileys)
- [Docker Healthcheck Best Practices](https://docs.docker.com/engine/reference/builder/#healthcheck)

---

**Próximos Passos Sugeridos:**
1. Testar criação de instância
2. Validar geração de QR code
3. Monitorar logs por 24h
4. Atualizar versão do WhatsApp Web se necessário (usar script)
