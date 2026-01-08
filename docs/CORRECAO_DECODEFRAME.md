# Correção do Erro decodeFrame na Evolution API

**Data:** 2025-01-05  
**Problema:** Erro `decodeFrame` impedindo geração de QR code  
**Status:** ✅ Correções aplicadas

## 🔍 Diagnóstico

O erro `decodeFrame` na Evolution API geralmente ocorre devido a:
1. **Incompatibilidade de versão** entre a API e o WhatsApp Web
2. **Versão desatualizada** da Evolution API
3. **Versão incorreta** do WhatsApp Web configurada
4. **Problemas de conexão** com o Redis

## ✅ Correções Aplicadas

### 1. Atualização da Evolution API

**Arquivo:** `Dockerfile.evolution`

**Mudança:**
- ❌ **Antes:** `FROM atendai/evolution-api:v2.2.3`
- ✅ **Depois:** `FROM atendai/evolution-api:latest`

**Motivo:** Versões desatualizadas são a causa mais comum de erros de conexão. A tag `latest` garante atualizações automáticas.

### 2. Configuração da Versão do WhatsApp Web

**Arquivo:** `docker-compose.yml`

**Mudança:**
- ❌ **Antes:** `CONFIG_SESSION_PHONE_VERSION` estava comentado
- ✅ **Depois:** `CONFIG_SESSION_PHONE_VERSION: 2.2413.51`

**Versão obtida de:** https://web.whatsapp.com/check-update?version=0&platform=web  
**Data da verificação:** 2025-01-05

**Motivo:** O erro `decodeFrame` é frequentemente um sintoma de que a versão do WhatsApp Web utilizada pela API está desatualizada.

### 3. Verificação do Redis

**Status:** ✅ Configuração correta

A configuração do Redis está adequada:
```yaml
CACHE_REDIS_ENABLED: true
CACHE_REDIS_URI: redis://redis:6379/0
```

O Redis está configurado para usar o nome do serviço `redis` do docker-compose, o que é a forma correta de comunicação entre containers.

## 📋 Próximos Passos

### 1. Reconstruir a Imagem Docker

```bash
cd /root/Core_SinapUm/services/evolution_api_service
docker compose build evolution-api
```

### 2. Parar os Containers

```bash
docker compose down
```

### 3. Iniciar os Containers

```bash
docker compose up -d
```

### 4. Verificar os Logs

```bash
docker compose logs -f evolution-api
```

### 5. Testar a Geração de QR Code

Após os containers iniciarem, teste a criação de uma nova instância e verifique se o QR code é gerado corretamente.

## 🔄 Como Atualizar a Versão do WhatsApp Web no Futuro

Quando o erro `decodeFrame` voltar a aparecer, siga estes passos:

1. **Obter a versão atual do WhatsApp Web:**
   ```bash
   curl -s "https://web.whatsapp.com/check-update?version=0&platform=web"
   ```

2. **Extrair o número da versão** do JSON retornado (campo `currentVersion`)

3. **Atualizar o `docker-compose.yml`:**
   ```yaml
   CONFIG_SESSION_PHONE_VERSION: <versão_obtida>
   ```

4. **Reiniciar os containers:**
   ```bash
   docker compose down
   docker compose up -d
   ```

## 📚 Referências

- [Issue #1656 - Endless synchronization with WhatsApp](https://github.com/EvolutionAPI/evolution-api/issues/1656)
- [Issue #1518 - Erro para gerar o QRCode](https://github.com/EvolutionAPI/evolution-api/issues/1518)
- [Issue #593 - Number keeps getting logged out](https://github.com/EvolutionAPI/evolution-api/issues/593)

## ⚠️ Observações Importantes

1. **Mantenha a API sempre atualizada:** O WhatsApp frequentemente atualiza seus protocolos de segurança, exigindo manutenção da API.

2. **Verifique regularmente a versão do WhatsApp Web:** A versão pode mudar a qualquer momento, causando incompatibilidades.

3. **Monitore os logs:** Após aplicar as correções, monitore os logs para verificar se o erro `decodeFrame` foi resolvido.

4. **Teste em ambiente isolado:** Se possível, teste as mudanças em um ambiente de desenvolvimento antes de aplicar em produção.

## ✅ Checklist de Verificação

- [x] Dockerfile atualizado para usar `latest`
- [x] `CONFIG_SESSION_PHONE_VERSION` configurado com versão atual (2.2413.51)
- [x] Redis configurado corretamente
- [ ] Imagem Docker reconstruída
- [ ] Containers reiniciados
- [ ] Logs verificados
- [ ] QR code testado e funcionando

---

**Última atualização:** 2025-01-05  
**Versão do WhatsApp Web configurada:** 2.2413.51  
**Versão da Evolution API:** latest (atendai/evolution-api:latest)
