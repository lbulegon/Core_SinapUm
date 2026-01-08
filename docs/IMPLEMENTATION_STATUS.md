# Status da Implementação - Nova Arquitetura WhatsApp

## ✅ Concluído

### 1. Inventário e Documentação
- [x] `existing_apps.md` - Apps Django existentes
- [x] `existing_endpoints.md` - Endpoints existentes
- [x] `risk_points.md` - Pontos de risco
- [x] `ARCHITECTURE_MAPPING.md` - Mapeamento antigo vs novo
- [x] `DEPRECATION_PLAN.md` - Plano de deprecação
- [x] `scripts/check_architecture.py` - Script de verificação

### 2. Apps Criados (Core_SinapUm)
- [x] `app_whatsapp_gateway` - Models e migrations
  - [x] `EvolutionInstance` (multi-tenant por shopper_id)
  - [x] `WebhookEvent` (log de eventos)
  - [x] Admin configurado
  - [x] Migrations criadas
  
- [x] `app_conversations` - Models e migrations
  - [x] `Conversation` (conversas multi-tenant)
  - [x] `Message` (mensagens normalizadas)
  - [x] `Suggestion` (sugestões de IA)
  - [x] Admin configurado
  - [x] Migrations criadas

- [x] `app_ai_bridge` - App criado
- [x] `app_mcp` - App criado

- [x] Apps adicionados ao `INSTALLED_APPS`

---

## ⏳ Pendente

### 3. Implementação de Views e Services

#### app_whatsapp_gateway
- [ ] `clients/evolution_client.py` - Cliente Evolution API multi-tenant
- [ ] `parsers/evolution_parser.py` - Parser de eventos Evolution → Evento Canônico
- [ ] `views.py` - Endpoints:
  - [ ] `POST /webhooks/evolution/<instance_id>/messages`
  - [ ] `POST /channels/whatsapp/send`
  - [ ] `POST /instances/evolution/create`
  - [ ] `GET /instances/evolution/<instance_id>/qr`
  - [ ] `POST /instances/evolution/<instance_id>/connect`
- [ ] `urls.py` - Rotas
- [ ] `services.py` - Services de negócio

#### app_conversations
- [ ] `services.py` - Services:
  - [ ] `ConversationService.get_or_create_by_inbound_event()`
  - [ ] `MessageService.store_inbound()`
  - [ ] `SuggestionService.create_from_ai()`
  - [ ] `SuggestionService.mark_sent()`
- [ ] `views.py` - Endpoints Console:
  - [ ] `GET /console/conversations?shopper_id=...`
  - [ ] `GET /console/conversations/<conversation_id>`
  - [ ] `GET /console/conversations/<conversation_id>/suggestions`
  - [ ] `POST /console/suggestions/<suggestion_id>/send`
  - [ ] `POST /console/messages/send`
- [ ] `urls.py` - Rotas

#### app_ai_bridge
- [ ] `clients/openmind_client.py` - Cliente OpenMind
- [ ] `views.py` - Endpoints:
  - [ ] `POST /ai/inbound` - Recebe evento canônico, chama OpenMind
  - [ ] `POST /ai/outbound` - Recebe resposta do OpenMind
- [ ] `urls.py` - Rotas

#### app_mcp
- [ ] `tools/` - Implementação de tools:
  - [ ] `customer.get_or_create()`
  - [ ] `catalog.search()`
  - [ ] `product.get()`
  - [ ] `cart.get()`
  - [ ] `cart.add()`
  - [ ] `order.create()`
  - [ ] `order.status()`
- [ ] `clients/vitrinezap_client.py` - Cliente VitrineZap API
- [ ] `views.py` - Endpoint:
  - [ ] `POST /mcp/tools/<tool_name>`
- [ ] `urls.py` - Rotas

### 4. Contrato de Evento Canônico
- [ ] `core/contracts/canonical_event.py` - Definição do contrato

### 5. Feature Flags
- [ ] Adicionar feature flags no `settings.py`:
  - [ ] `FEATURE_EVOLUTION_MULTI_TENANT`
  - [ ] `FEATURE_OPENMIND_ENABLED`
  - [ ] `FEATURE_CONSOLE_ENABLED`

### 6. Integração com URLs Principais
- [ ] Adicionar rotas no `setup/urls.py`:
  - [ ] `/webhooks/evolution/` → `app_whatsapp_gateway.urls`
  - [ ] `/console/` → `app_conversations.urls`
  - [ ] `/ai/` → `app_ai_bridge.urls`
  - [ ] `/mcp/` → `app_mcp.urls`

### 7. Évora/VitrineZap - app_console
- [ ] Criar app `app_console`
- [ ] Models (se necessário)
- [ ] Views e templates:
  - [ ] Dashboard de conversas
  - [ ] Detalhe de conversa
  - [ ] Lista de sugestões
- [ ] Cliente API do Core
- [ ] URLs

### 8. Testes
- [ ] Script `smoke_test_evolution_webhook.py`
- [ ] Script `smoke_test_suggestion_send.py`
- [ ] Testes manuais guiados

---

## 📝 Notas

- Todos os apps novos têm comentários `# ARQUITETURA NOVA` no topo
- Models seguem convenção de nomenclatura clara
- Migrations criadas e prontas para rodar
- Admin configurado para todos os models

---

**Última atualização:** 2026-01-03

