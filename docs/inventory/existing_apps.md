# Inventário de Apps Django Existentes

## Core_SinapUm

### Apps Instalados (INSTALLED_APPS)
1. **app_sinapum** - App principal do Core
   - Análise de imagens de produtos
   - Integração com Evolution API (WhatsApp)
   - Views: `views_evolution.py` para WhatsApp
   - Service: `evolution_service.py`
   
2. **app_mcp_tool_registry** - Registry de ferramentas MCP
   - Sistema de registro de tools para IA
   
3. **app_ifood_integration** - Integração com iFood
   - API interna para integração iFood
   
4. **app_leads** - Lead Registry
   - Sistema central de captação de leads
   - Endpoints: `/api/leads/`

### URLs Principais (setup/urls.py)
- `/whatsapp/` - Conectar WhatsApp
- `/whatsapp/api/create-instance/` - Criar instância Evolution
- `/whatsapp/api/get-qrcode/` - Obter QR Code
- `/whatsapp/api/get-status/` - Status da instância
- `/whatsapp/api/delete-instance/` - Deletar instância
- `/whatsapp/api/restart-instance/` - Reiniciar instância
- `/core/` - MCP Tool Registry
- `/api/v1/analyze-product-image` - Análise de imagens

---

## Évora/VitrineZap

### Apps Instalados (INSTALLED_APPS)
1. **app_marketplace** - Marketplace principal
   - Modelos: Cliente, PersonalShopper, AddressKeeper
   - Modelos WhatsApp: WhatsappGroup, WhatsappParticipant, WhatsappConversation
   - WhatsAppFlowEngine - Engine de fluxo conversacional
   
2. **app_whatsapp_integration** - Integração WhatsApp (ATIVO)
   - **Models:**
     - `WhatsAppContact` - Contatos WhatsApp vinculados
     - `WhatsAppMessageLog` - Logs de mensagens
     - `EvolutionInstance` - Instâncias Evolution API
     - `EvolutionMessage` - Mensagens Evolution
   - **Views:**
     - `webhook_evolution_api` - Recebe webhooks da Evolution
     - `webhook_from_gateway` - Recebe mensagens do gateway
     - `send_message` - Enviar mensagem
     - `send_product` - Enviar produto
     - `instance_status` - Status da instância
     - `get_qrcode` - Obter QR Code
     - `connect_instance` - Conectar instância
   - **Service:**
     - `EvolutionAPIService` - Cliente Evolution API
   
3. **app_settlement** - Settlement & Ledger
   - Sistema de liquidação
   
4. **app_shopperbot_integration** - Integração ShopperBot
   - Integração com serviço ShopperBot do Core

### URLs Principais (setup/urls.py)
- `/api/whatsapp/webhook/evolution/` - Webhook Evolution API
- `/api/whatsapp/webhook-from-gateway/` - Webhook do gateway
- `/api/whatsapp/send/` - Enviar mensagem
- `/api/whatsapp/send-product/` - Enviar produto
- `/api/whatsapp/status/` - Status da instância
- `/api/whatsapp/qrcode/` - Obter QR Code
- `/api/whatsapp/connect/` - Conectar instância

### App Separado (não instalado no Django)
- **app_vz_whatsapp_gateway** - Gateway separado (provavelmente serviço standalone)

---

## Configurações de Ambiente

### Core_SinapUm
- Evolution API: Configurado em `app_sinapum/evolution_service.py`
- Base URL padrão: `http://69.169.102.84:8004`
- Instance padrão: `default` ou `core_sinapum`

### Évora/VitrineZap
- Evolution API URL: `EVOLUTION_API_URL` (default: `http://69.169.102.84:8004`)
- Evolution API Key: `EVOLUTION_API_KEY`
- Instance Name: `EVOLUTION_INSTANCE_NAME` (default: `default`)
- OpenMind AI: Configurado com URL e chave
- ShopperBot: Configurado com base URL e timeout

---

## Observações Importantes

1. **Já existe integração Evolution no Évora** via `app_whatsapp_integration`
2. **Já existe integração Evolution no Core** via `app_sinapum/views_evolution.py`
3. **Modelos de mensagens já existem** no Évora:
   - `EvolutionMessage` - Mensagens Evolution
   - `WhatsAppMessageLog` - Logs de mensagens
   - `EvolutionInstance` - Instâncias
4. **Fluxo conversacional já existe** via `WhatsAppFlowEngine`
5. **Webhook receiver já existe** em `/api/whatsapp/webhook/evolution/`

