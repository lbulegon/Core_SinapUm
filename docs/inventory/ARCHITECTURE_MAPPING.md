# Mapeamento de Arquitetura - Antigo vs Novo

## 🎯 Objetivo
Este documento mapeia **exatamente** o que é código antigo (não tocar) vs código novo (nova arquitetura) para evitar confusão.

---

## 📊 VISÃO GERAL

### Arquitetura ANTIGA (NÃO MODIFICAR)
- **Évora/VitrineZap**: `app_whatsapp_integration` - Recebe webhooks, processa mensagens
- **Core_SinapUm**: `app_sinapum/views_evolution.py` - Endpoints básicos Evolution
- **Fluxo**: Evolution → Évora webhook → Processamento direto → Resposta automática

### Arquitetura NOVA (IMPLEMENTAR)
- **Core_SinapUm**: `app_whatsapp_gateway` - Gateway centralizado multi-tenant
- **Core_SinapUm**: `app_conversations` - Conversas e sugestões
- **Core_SinapUm**: `app_ai_bridge` - Ponte com OpenMind
- **Core_SinapUm**: `app_mcp` - Tools para IA
- **Évora/VitrineZap**: `app_console` - UI de conversas
- **Fluxo**: Evolution → Core webhook → Normalização → OpenMind → Sugestões → Console

---

## 📁 MAPEAMENTO DE ARQUIVOS

### ÉVORA/VITRINEZAP - ANTIGO (MANTER)

| Arquivo | Status | Uso Atual | Ação |
|---------|--------|-----------|------|
| `app_whatsapp_integration/models.py` | ✅ **ATIVO** | Models: EvolutionMessage, WhatsAppMessageLog | **NÃO MODIFICAR** |
| `app_whatsapp_integration/views.py` | ✅ **ATIVO** | Webhook receiver, send_message | **NÃO MODIFICAR** |
| `app_whatsapp_integration/evolution_service.py` | ✅ **ATIVO** | Cliente Evolution API | **NÃO MODIFICAR** |
| `app_whatsapp_integration/urls.py` | ✅ **ATIVO** | URLs: `/api/whatsapp/*` | **NÃO MODIFICAR** |
| `app_marketplace/whatsapp_flow_engine.py` | ✅ **ATIVO** | Processamento automático | **NÃO MODIFICAR** |

### CORE_SINAPUM - ANTIGO (MANTER)

| Arquivo | Status | Uso Atual | Ação |
|---------|--------|-----------|------|
| `app_sinapum/views_evolution.py` | ✅ **ATIVO** | Endpoints: `/whatsapp/api/*` | **NÃO MODIFICAR** |
| `app_sinapum/evolution_service.py` | ✅ **ATIVO** | Service Evolution | **NÃO MODIFICAR** |

### CORE_SINAPUM - NOVO (CRIAR)

| App | Arquivos | Propósito | Diferença do Antigo |
|-----|----------|----------|---------------------|
| `app_whatsapp_gateway` | `models.py`, `views.py`, `clients/evolution_client.py` | Gateway multi-tenant | **Multi-tenant por shopper_id** vs instância única |
| `app_conversations` | `models.py`, `views.py`, `services.py` | Conversas e sugestões | **Novo modelo** vs EvolutionMessage antigo |
| `app_ai_bridge` | `views.py`, `clients/openmind_client.py` | Ponte OpenMind | **Novo** - não existe no antigo |
| `app_mcp` | `views.py`, `tools/` | Tools para IA | **Novo** - não existe no antigo |

### ÉVORA/VITRINEZAP - NOVO (CRIAR)

| App | Arquivos | Propósito | Diferença do Antigo |
|-----|----------|----------|---------------------|
| `app_console` | `models.py`, `views.py`, `templates/`, `clients/core_client.py` | UI de conversas | **Novo** - console não existe no antigo |

---

## 🔀 ENDPOINTS - ANTIGO vs NOVO

### ANTIGO (MANTER FUNCIONANDO)

#### Évora
- `/api/whatsapp/webhook/evolution/` → `app_whatsapp_integration.views.webhook_evolution_api`
- `/api/whatsapp/send/` → `app_whatsapp_integration.views.send_message`
- `/api/whatsapp/send-product/` → `app_whatsapp_integration.views.send_product`
- `/api/whatsapp/qrcode/` → `app_whatsapp_integration.views.get_qrcode`
- `/api/whatsapp/connect/` → `app_whatsapp_integration.views.connect_instance`

#### Core
- `/whatsapp/api/create-instance/` → `app_sinapum.views_evolution.whatsapp_create_instance`
- `/whatsapp/api/get-qrcode/` → `app_sinapum.views_evolution.whatsapp_get_qrcode`
- `/whatsapp/api/get-status/` → `app_sinapum.views_evolution.whatsapp_get_status`

### NOVO (CRIAR)

#### Core - Gateway
- `/webhooks/evolution/<instance_id>/messages` → `app_whatsapp_gateway.views.webhook_receiver`
- `/channels/whatsapp/send` → `app_whatsapp_gateway.views.send_message`
- `/instances/evolution/create` → `app_whatsapp_gateway.views.create_instance`
- `/instances/evolution/<instance_id>/qr` → `app_whatsapp_gateway.views.get_qr`
- `/instances/evolution/<instance_id>/connect` → `app_whatsapp_gateway.views.connect`

#### Core - Console API
- `/console/conversations?shopper_id=...` → `app_conversations.views.list_conversations`
- `/console/conversations/<conversation_id>` → `app_conversations.views.get_conversation`
- `/console/conversations/<conversation_id>/suggestions` → `app_conversations.views.get_suggestions`
- `/console/suggestions/<suggestion_id>/send` → `app_conversations.views.send_suggestion`
- `/console/messages/send` → `app_conversations.views.send_message`

#### Core - AI Bridge
- `/ai/inbound` → `app_ai_bridge.views.inbound`
- `/ai/outbound` → `app_ai_bridge.views.outbound`

#### Core - MCP Tools
- `/mcp/tools/<tool_name>` → `app_mcp.views.execute_tool`

#### Évora - Console UI
- `/console/` → `app_console.views.dashboard`
- `/console/conversations/` → `app_console.views.conversations`
- `/console/conversations/<id>/` → `app_console.views.conversation_detail`

---

## 🗄️ MODELS - ANTIGO vs NOVO

### ANTIGO (NÃO MODIFICAR)

#### Évora - `app_whatsapp_integration`
- `EvolutionInstance` - Instância Evolution (instância única)
- `EvolutionMessage` - Mensagens Evolution
- `WhatsAppContact` - Contatos WhatsApp
- `WhatsAppMessageLog` - Logs de mensagens

### NOVO (CRIAR)

#### Core - `app_whatsapp_gateway`
- `EvolutionInstance` - Instância Evolution (**multi-tenant por shopper_id**)
  - Diferença: Adiciona campo `shopper_id` e suporte multi-tenant

#### Core - `app_conversations`
- `Conversation` - Conversa por shopper (**novo modelo**)
- `Message` - Mensagem normalizada (**novo modelo**)
- `Suggestion` - Sugestão de IA (**novo modelo**)

---

## 🔧 SERVICES - ANTIGO vs NOVO

### ANTIGO (MANTER)

#### Évora
- `EvolutionAPIService` - Cliente Evolution (instância única)
  - `send_text_message(phone, message, instance_name=None)`
  - `send_product_message(phone, product_data, image_url)`
  - `get_qrcode(instance_name)`
  - `create_instance(instance_name)`

### NOVO (CRIAR)

#### Core
- `EvolutionClient` - Cliente Evolution (**multi-tenant**)
  - `send_text(instance_id, to, text)` - **Diferença: usa instance_id**
  - `send_media(instance_id, to, media_url, caption)`
  - `get_qr(instance_id)` - **Diferença: usa instance_id**
  - `create_instance(shopper_id, instance_id)` - **Diferença: cria por shopper**

---

## 🏷️ CONVENÇÕES DE NOMENCLATURA

### Prefixos para Identificar

#### ANTIGO (Legacy)
- **Évora**: `app_whatsapp_integration.*` - Tudo com este prefixo é ANTIGO
- **Core**: `app_sinapum.views_evolution.*` - Tudo com este prefixo é ANTIGO
- **URLs**: `/api/whatsapp/*` (Évora) e `/whatsapp/api/*` (Core) - ANTIGO

#### NOVO (Nova Arquitetura)
- **Core**: `app_whatsapp_gateway.*` - Tudo com este prefixo é NOVO
- **Core**: `app_conversations.*` - Tudo com este prefixo é NOVO
- **Core**: `app_ai_bridge.*` - Tudo com este prefixo é NOVO
- **Core**: `app_mcp.*` - Tudo com este prefixo é NOVO
- **Évora**: `app_console.*` - Tudo com este prefixo é NOVO
- **URLs**: `/webhooks/evolution/*`, `/console/*`, `/ai/*`, `/mcp/*` - NOVO

---

## 🚩 FEATURE FLAGS

### Flags de Controle

```python
# settings.py

# Ativar nova arquitetura (gradualmente)
FEATURE_EVOLUTION_MULTI_TENANT = os.getenv('FEATURE_EVOLUTION_MULTI_TENANT', 'false').lower() == 'true'
FEATURE_OPENMIND_ENABLED = os.getenv('FEATURE_OPENMIND_ENABLED', 'false').lower() == 'true'
FEATURE_CONSOLE_ENABLED = os.getenv('FEATURE_CONSOLE_ENABLED', 'false').lower() == 'true'

# Deprecar arquitetura antiga (futuro)
FEATURE_DEPRECATE_LEGACY_WHATSAPP = os.getenv('FEATURE_DEPRECATE_LEGACY_WHATSAPP', 'false').lower() == 'true'
```

### Como Usar

```python
# Em views/urls
if settings.FEATURE_EVOLUTION_MULTI_TENANT:
    # Usar nova arquitetura
    from app_whatsapp_gateway.views import webhook_receiver
else:
    # Usar arquitetura antiga
    from app_whatsapp_integration.views import webhook_evolution_api
```

---

## 📝 DOCUMENTAÇÃO DE CÓDIGO

### Comentários Obrigatórios

```python
# ============================================================================
# ARQUITETURA NOVA - app_whatsapp_gateway
# ============================================================================
# Este módulo faz parte da NOVA arquitetura multi-tenant.
# 
# ANTIGO (não usar): app_whatsapp_integration (Évora)
# NOVO (usar): app_whatsapp_gateway (Core)
#
# Diferenças:
# - Multi-tenant por shopper_id
# - Normalização de eventos
# - Integração com OpenMind
# ============================================================================
```

---

## 🔄 ESTRATÉGIA DE MIGRAÇÃO

### Fase 1: Coexistência (ATUAL)
- ✅ Antigo funciona normalmente
- ✅ Novo implementado em paralelo
- ✅ Feature flags desabilitadas por padrão

### Fase 2: Teste Gradual
- ✅ Habilitar feature flag para 1 shopper
- ✅ Testar nova arquitetura
- ✅ Comparar resultados

### Fase 3: Migração
- ✅ Migrar shopper por shopper
- ✅ Desabilitar antigo quando migrado

### Fase 4: Deprecação
- ✅ Marcar código antigo como deprecated
- ✅ Remover código antigo (após 100% migrado)

---

## ✅ CHECKLIST DE DIFERENCIAÇÃO

Ao criar código novo, sempre:

- [ ] Usar prefixo `app_whatsapp_gateway`, `app_conversations`, etc. (NOVO)
- [ ] Adicionar comentário `# ARQUITETURA NOVA` no topo do arquivo
- [ ] Documentar diferenças do código antigo
- [ ] Usar feature flags para ativação
- [ ] Não modificar código com prefixo `app_whatsapp_integration` (ANTIGO)
- [ ] Não modificar `app_sinapum.views_evolution` (ANTIGO)
- [ ] Usar URLs com prefixos `/webhooks/`, `/console/`, `/ai/`, `/mcp/` (NOVO)
- [ ] Não usar URLs `/api/whatsapp/*` ou `/whatsapp/api/*` (ANTIGO)

---

## 📚 REFERÊNCIA RÁPIDA

| Item | ANTIGO | NOVO |
|------|--------|------|
| **App Évora** | `app_whatsapp_integration` | `app_console` |
| **App Core** | `app_sinapum.views_evolution` | `app_whatsapp_gateway`, `app_conversations`, `app_ai_bridge`, `app_mcp` |
| **Webhook** | `/api/whatsapp/webhook/evolution/` | `/webhooks/evolution/<instance_id>/messages` |
| **Enviar** | `/api/whatsapp/send/` | `/channels/whatsapp/send` |
| **Models** | `EvolutionMessage` (Évora) | `Message` (Core) |
| **Instance** | Instância única | Multi-tenant por shopper_id |
| **Processamento** | Direto no webhook | Normalização → OpenMind → Sugestões |

---

**Última atualização:** 2026-01-03  
**Mantido por:** Equipe de Desenvolvimento

