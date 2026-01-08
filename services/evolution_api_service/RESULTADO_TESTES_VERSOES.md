# Resultado dos Testes de Versões - CONFIG_SESSION_PHONE_VERSION

**Data:** 2026-01-05  
**Objetivo:** Testar diferentes versões do WhatsApp Web para resolver erro `decodeFrame`

## 🧪 Versões Testadas

### 1. ✅ Versão do check-update: `2.2413.51`
- **Status:** ❌ Não funcionou
- **QR Count:** 0
- **Erro decodeFrame:** Presente

### 2. ❌ Auto-detecção (sem CONFIG_SESSION_PHONE_VERSION)
- **Status:** ❌ Não funcionou
- **QR Count:** 0
- **Erro decodeFrame:** Presente
- **Observação:** Evolution API v2.2.3 não detectou automaticamente

### 3. ❌ Versão alternativa: `2.3000.1015901307`
- **Status:** ❌ Não funcionou
- **QR Count:** 0
- **Erro decodeFrame:** Presente
- **Observação:** Versão mencionada em issues do Reddit/GitHub

## 📊 Comparação dos Testes

| Versão | QR Gerado | Erro decodeFrame | Conclusão |
|--------|-----------|------------------|-----------|
| `2.2413.51` | ❌ count: 0 | ❌ Presente | Não resolve |
| Auto-detecção | ❌ count: 0 | ❌ Presente | Não funciona em v2.2.3 |
| `2.3000.1015901307` | ❌ count: 0 | ❌ Presente | Não resolve |

## 🔍 Análise

### Problema Identificado

O erro `decodeFrame` **não está relacionado à versão do WhatsApp Web** nas versões testadas. O problema é mais profundo:

1. **Evolution API v2.2.3** pode ter bug conhecido
2. **Baileys** pode estar desatualizado na v2.2.3
3. **Problema de rede/firewall** pode estar impedindo conexão
4. **Incompatibilidade** entre Evolution API e WhatsApp Web atual

### Evidências

- Todas as versões testadas apresentam o mesmo erro
- QR code não é gerado em nenhum caso
- Erro `decodeFrame` persiste independente da versão

## 💡 Recomendações

### 1. Atualizar Evolution API para Versão Mais Recente

A pesquisa mostrou que **Evolution API v2.3.5** resolve o problema:
- Inclui correções para geração de QR code
- Atualiza Baileys para v7.0.0-rc.5
- Remove necessidade de `CONFIG_SESSION_PHONE_VERSION`

**Imagem recomendada:**
```yaml
image: evoapicloud/evolution-api:v2.3.5
```

### 2. Verificar Conectividade de Rede

```bash
docker exec evolution-api wget -O- https://web.whatsapp.com 2>&1 | head -10
```

### 3. Considerar Imagem Alternativa

```yaml
image: evoapicloud/evolution-api:homolog
```

## 📋 Próximos Passos

1. **Atualizar Evolution API para v2.3.5 ou mais recente**
2. **Remover CONFIG_SESSION_PHONE_VERSION** (não é mais necessário)
3. **Testar novamente** criação de instância e QR code

## 🔧 Comando para Atualizar

```bash
cd /root/Core_SinapUm/services/evolution_api_service

# Atualizar docker-compose.yml para usar v2.3.5
# Alterar: image: evoapicloud/evolution-api:v2.3.5
# Remover: CONFIG_SESSION_PHONE_VERSION

docker compose down
docker compose build evolution-api
docker compose up -d
```

---

**Conclusão:** O problema não está na versão do WhatsApp Web, mas na versão da Evolution API (v2.2.3). Recomenda-se atualizar para v2.3.5 ou mais recente.
