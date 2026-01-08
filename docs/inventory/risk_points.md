# Pontos de Risco - Onde Mudanças Podem Quebrar o Sistema

## 🔴 RISCO CRÍTICO - NÃO MODIFICAR

### 1. Webhook Evolution API (Évora)
**Arquivo:** `/root/Source/evora/app_whatsapp_integration/views.py`  
**Função:** `webhook_evolution_api`  
**Endpoint:** `/api/whatsapp/webhook/evolution/`

**Riscos:**
- ⚠️ Este endpoint está **ATIVO** e recebendo mensagens reais
- ⚠️ Qualquer modificação pode quebrar o recebimento de mensagens
- ⚠️ Processa eventos `messages.upsert` e `qrcode.updated`
- ⚠️ Salva mensagens em `EvolutionMessage` e `WhatsAppMessageLog`
- ⚠️ Integrado com `WhatsAppFlowEngine` para processamento automático

**Ação Recomendada:**
- ✅ Criar **novo endpoint** para nova arquitetura: `/webhooks/evolution/<instance_id>/messages`
- ✅ Manter endpoint antigo funcionando
- ✅ Adicionar feature flag para rotear entre antigo/novo
- ✅ Migrar gradualmente

---

### 2. Models de Mensagens (Évora)
**Arquivos:**
- `/root/Source/evora/app_whatsapp_integration/models.py`
  - `EvolutionMessage`
  - `WhatsAppMessageLog`
  - `EvolutionInstance`
  - `WhatsAppContact`

**Riscos:**
- ⚠️ Models já estão em uso e têm dados em produção
- ⚠️ Qualquer alteração de schema pode quebrar queries existentes
- ⚠️ Foreign keys já estabelecidas

**Ação Recomendada:**
- ✅ **NÃO modificar** models existentes
- ✅ Criar **novos models** no Core_SinapUm:
  - `app_conversations.Conversation`
  - `app_conversations.Message`
  - `app_conversations.Suggestion`
- ✅ Criar **adapter** para migrar dados se necessário

---

### 3. WhatsAppFlowEngine (Évora)
**Arquivo:** `/root/Source/evora/app_marketplace/whatsapp_flow_engine.py`  
**Uso:** Processamento automático de mensagens

**Riscos:**
- ⚠️ Engine já processa mensagens automaticamente
- ⚠️ Envia respostas automáticas
- ⚠️ Integrado com grupos e conversas privadas

**Ação Recomendada:**
- ✅ **NÃO remover** ou modificar engine existente
- ✅ Criar **nova camada** de processamento no Core
- ✅ Adicionar feature flag para escolher engine antiga/nova
- ✅ Gradualmente migrar para nova arquitetura

---

### 4. EvolutionAPIService (Évora)
**Arquivo:** `/root/Source/evora/app_whatsapp_integration/evolution_service.py`  
**Uso:** Cliente Evolution API

**Riscos:**
- ⚠️ Service já está sendo usado para enviar mensagens
- ⚠️ Métodos: `send_text_message()`, `send_product_message()`, `get_qrcode()`, etc.

**Ação Recomendada:**
- ✅ **NÃO remover** service existente
- ✅ Criar **novo EvolutionClient** no Core_SinapUm
- ✅ Reutilizar lógica se possível
- ✅ Adicionar suporte multi-tenant (por shopper_id)

---

### 5. Endpoints de Envio (Évora)
**Endpoints:**
- `/api/whatsapp/send/`
- `/api/whatsapp/send-product/`
- `/api/whatsapp/connect/`
- `/api/whatsapp/qrcode/`

**Riscos:**
- ⚠️ Endpoints já estão em uso pelo frontend
- ⚠️ Qualquer modificação pode quebrar integrações existentes

**Ação Recomendada:**
- ✅ **NÃO remover** endpoints existentes
- ✅ Criar **novos endpoints** no Core:
  - `/channels/whatsapp/send`
  - `/instances/evolution/create`
  - `/instances/evolution/<instance_id>/qr`
- ✅ Adicionar feature flag para rotear entre antigo/novo

---

## 🟡 RISCO MÉDIO - CUIDADO

### 6. URLs do Core (Core_SinapUm)
**Arquivo:** `/root/Core_SinapUm/setup/urls.py`

**Riscos:**
- ⚠️ URLs `/whatsapp/*` já estão definidas
- ⚠️ Views `views_evolution.py` já existem

**Ação Recomendada:**
- ✅ Adicionar novas URLs **sem remover** as antigas
- ✅ Usar prefixos diferentes: `/webhooks/`, `/instances/`, `/console/`

---

### 7. Settings e Configurações
**Arquivos:**
- `/root/Core_SinapUm/setup/settings.py`
- `/root/Source/evora/setup/settings.py`

**Riscos:**
- ⚠️ Variáveis de ambiente já configuradas
- ⚠️ `EVOLUTION_API_URL`, `EVOLUTION_API_KEY` já em uso

**Ação Recomendada:**
- ✅ Adicionar **novas variáveis** sem remover as antigas
- ✅ Usar feature flags: `FEATURE_EVOLUTION_MULTI_TENANT`, `FEATURE_OPENMIND_ENABLED`

---

### 8. Models do Marketplace (Évora)
**Arquivos:**
- `/root/Source/evora/app_marketplace/models.py`
  - `WhatsappGroup`
  - `WhatsappParticipant`
  - `WhatsappConversation`

**Riscos:**
- ⚠️ Models já estão em uso
- ⚠️ Relacionados com `WhatsAppFlowEngine`

**Ação Recomendada:**
- ✅ **NÃO modificar** models existentes
- ✅ Criar **novos models** no Core para nova arquitetura
- ✅ Criar **adapter** se precisar migrar dados

---

## 🟢 RISCO BAIXO - PODE MODIFICAR COM CUIDADO

### 9. Templates e Frontend
**Riscos:**
- ⚠️ Templates podem estar usando endpoints antigos

**Ação Recomendada:**
- ✅ Adicionar **novos templates** para console
- ✅ Manter templates antigos funcionando
- ✅ Adicionar feature flag no frontend

---

### 10. Migrations
**Riscos:**
- ⚠️ Migrations existentes não devem ser modificadas

**Ação Recomendada:**
- ✅ Criar **novas migrations** apenas
- ✅ **NÃO modificar** migrations antigas
- ✅ Usar `RunPython` se precisar migrar dados

---

## 📋 CHECKLIST DE SEGURANÇA

Antes de fazer qualquer modificação:

- [ ] Verificar se endpoint/model está em uso em produção
- [ ] Criar novo endpoint/model em vez de modificar existente
- [ ] Adicionar feature flag para ativar gradualmente
- [ ] Manter backward compatibility
- [ ] Testar em ambiente de desenvolvimento primeiro
- [ ] Documentar mudanças
- [ ] Criar adapter/migração se necessário

---

## 🎯 ESTRATÉGIA RECOMENDADA

1. **Criar tudo novo** no Core_SinapUm:
   - `app_whatsapp_gateway` (novo)
   - `app_conversations` (novo)
   - `app_ai_bridge` (novo)
   - `app_mcp` (novo)

2. **Manter tudo existente** funcionando:
   - Endpoints antigos do Évora
   - Models antigos do Évora
   - Services antigos do Évora

3. **Adicionar feature flags**:
   - `FEATURE_EVOLUTION_MULTI_TENANT`
   - `FEATURE_OPENMIND_ENABLED`
   - `FEATURE_CONSOLE_ENABLED`

4. **Migrar gradualmente**:
   - Testar nova arquitetura em paralelo
   - Migrar shopper por shopper
   - Desativar arquitetura antiga quando estável

