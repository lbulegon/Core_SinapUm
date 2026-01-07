# Comando de Diagnóstico WhatsApp

## 📋 Visão Geral

O comando `whatsapp_diagnose` verifica o estado das integrações WhatsApp no Core_SinapUm / VitrineZap, garantindo que o sistema pode operar em **SHADOW MODE** sem quebrar nada.

**Regra máxima:**
- ✅ NÃO altera comportamento existente
- ✅ NÃO envia mensagens reais
- ✅ NÃO intercepta webhooks
- ✅ Apenas LÊ, VALIDA e REPORTA

## 🚀 Como Usar

### Comando Básico

```bash
python manage.py whatsapp_diagnose
```

### Modo Verbose

```bash
python manage.py whatsapp_diagnose --verbose
```

## 📊 O que o Comando Verifica

### [ENV] Variáveis de Ambiente

Verifica se as seguintes variáveis estão definidas:

- `WHATSAPP_PROVIDER` - Provider selecionado (simulated|cloud|baileys|evolution)
- `WHATSAPP_GATEWAY_PROVIDER` - Provider do gateway (legacy|simulated|noop|evolution|cloud|baileys)
- `WHATSAPP_SEND_ENABLED` - Se envio de mensagens está habilitado
- `WHATSAPP_SHADOW_MODE` - Se modo shadow está ativo
- `WHATSAPP_CANONICAL_EVENTS_ENABLED` - Se eventos canônicos estão habilitados
- `WHATSAPP_CANONICAL_SHADOW_MODE` - Se shadow mode de eventos canônicos está ativo
- `WHATSAPP_ROUTING_ENABLED` - Se roteamento está habilitado
- `WHATSAPP_SIM_ENABLED` - Se simulador está habilitado

**Status:**
- ✅ OK: Todas as variáveis definidas
- ⚠ WARN: Algumas variáveis não definidas
- ✗ FAIL: Variáveis críticas faltando

### [PROVIDER] Provider Ativo

Verifica:
- Qual provider está selecionado
- Se o provider responde ao `healthcheck()`
- Se `WHATSAPP_SEND_ENABLED` está habilitado
- Se `WHATSAPP_SHADOW_MODE` está ativo
- Lista de shoppers habilitados

**Status:**
- ✅ OK: Provider saudável e configurado corretamente
- ⚠ WARN: Provider configurado mas com avisos (ex: send habilitado em dev)
- ✗ FAIL: Provider não disponível ou não saudável

### [SHADOW MODE] Modo Shadow e Publisher Canônico

Verifica:
- Se shadow mode de eventos canônicos está ativo
- Se eventos canônicos estão habilitados
- Se o publisher canônico está inicializável

**Status:**
- ✅ OK: Shadow mode ativo e publisher disponível
- ⚠ WARN: Shadow mode desabilitado ou eventos canônicos desabilitados
- ✗ FAIL: Publisher não disponível ou erro ao inicializar

### [WEBHOOK] Endpoints de Webhook

Verifica:
- Se endpoints de webhook estão registrados em `urls.py`
- Lista de endpoints encontrados

**Nota:** Apenas validação local. Não faz chamadas externas.

**Status:**
- ✅ OK: Endpoints encontrados
- ⚠ WARN: Nenhum endpoint encontrado
- ✗ FAIL: Erro ao verificar endpoints

### [DATABASE] Tabelas de Banco de Dados

Verifica:
- Se tabelas existem:
  - `app_whatsapp_events_eventlog` (WhatsAppEventLog)
  - `app_whatsapp_events_conversation` (WhatsAppConversation)
  - `core_whatsapp_canonical_event_log` (CanonicalEventLog)
  - `core_whatsapp_simulated_message` (SimulatedMessage)
- Contagem de eventos recentes (últimas 24h)
- Contagem de conversas
- Contagem de mensagens simuladas

**Status:**
- ✅ OK: Tabelas existem e têm dados
- ⚠ WARN: Tabelas existem mas com erros ao contar
- ✗ FAIL: Tabelas não existem (precisa rodar migrations)

### [SIMULATOR] Simulador de Mensagens

Verifica:
- Se simulador está habilitado (`WHATSAPP_SIM_ENABLED`)
- Quantidade de mensagens simuladas no banco

**Status:**
- ✅ OK: Simulador habilitado e funcionando
- ⚠ WARN: Simulador desabilitado
- ✗ FAIL: Erro ao verificar simulador

## 📝 Formato da Saída

### Cabeçalho

```
======================================================================
WhatsApp Integration Diagnostic - 2026-01-XX XX:XX:XX
Environment: production (PRODUCTION)
======================================================================
```

### Seções

Cada seção mostra:
- ✅ OK: Tudo funcionando
- ⚠ WARN: Avisos (não crítico)
- ✗ FAIL: Falhas (crítico)

### Resumo Final

```
======================================================================
RESUMO
======================================================================

✓ OK: 8
⚠ WARN: 2
✗ FAIL: 0

Avisos:
  ⚠ WHATSAPP_SEND_ENABLED: True (mensagens serão enviadas)
  ⚠ Shadow mode desabilitado

Recomendações:
  → Para testar em dev, defina WHATSAPP_SEND_ENABLED=False
  → Para testar sem enviar mensagens, defina WHATSAPP_SHADOW_MODE=True
```

### Linha Final

```
✓ Diagnóstico concluído — nenhuma ação executada
```

## 🔍 Interpretando os Resultados

### ✅ OK (Verde)

Tudo funcionando corretamente. Sistema pronto para operar.

### ⚠ WARN (Amarelo)

Avisos não críticos. Sistema pode funcionar, mas recomenda-se ajustar configurações.

**Exemplos:**
- `WHATSAPP_SEND_ENABLED=True` em ambiente de desenvolvimento
- Shadow mode desabilitado
- Nenhum shopper habilitado

### ✗ FAIL (Vermelho)

Falhas críticas. Sistema pode não funcionar corretamente.

**Exemplos:**
- Provider não disponível
- Tabelas de banco não existem
- Publisher canônico não inicializável

## 🛠️ Quando Rodar

### Antes de Deploy

```bash
python manage.py whatsapp_diagnose
```

Verifica se tudo está configurado corretamente antes de fazer deploy.

### Após Mudanças de Configuração

```bash
python manage.py whatsapp_diagnose --verbose
```

Verifica se as mudanças de configuração foram aplicadas corretamente.

### Troubleshooting

```bash
python manage.py whatsapp_diagnose
```

Identifica problemas de configuração ou integração.

### Validação em CI/CD

```bash
python manage.py whatsapp_diagnose
```

Pode ser usado em pipelines de CI/CD para validar configuração antes de deploy.

## 🔒 Segurança

O comando **NUNCA** exibe:
- Tokens
- Segredos
- API Keys
- Payloads sensíveis

Valores sensíveis são mascarados como `*** (oculto)`.

## 📚 Exemplo de Saída Completa

```
======================================================================
WhatsApp Integration Diagnostic - 2026-01-05 14:30:00
Environment: development (DEBUG)
======================================================================

[ENV] Variáveis de Ambiente
----------------------------------------------------------------------
  ✓ WHATSAPP_PROVIDER: simulated
  ✓ WHATSAPP_GATEWAY_PROVIDER: simulated
  ✓ WHATSAPP_SEND_ENABLED: False
  ✓ WHATSAPP_SHADOW_MODE: True
  ✓ WHATSAPP_CANONICAL_EVENTS_ENABLED: True
  ✓ WHATSAPP_CANONICAL_SHADOW_MODE: True
  ✓ WHATSAPP_ROUTING_ENABLED: False
  ✓ WHATSAPP_SIM_ENABLED: True

[PROVIDER] Provider Ativo
----------------------------------------------------------------------
  ✓ Provider selecionado: simulated
  ✓ WHATSAPP_SEND_ENABLED: False (modo seguro)
  ✓ WHATSAPP_SHADOW_MODE: True (modo shadow ativo)
  ⚠ Nenhum shopper habilitado (WHATSAPP_ENABLED_SHOPPERS vazio)
  ✓ Provider saudável: Simulated provider is healthy

[SHADOW MODE] Modo Shadow e Publisher Canônico
----------------------------------------------------------------------
  ✓ WHATSAPP_CANONICAL_SHADOW_MODE: True
  ✓ WHATSAPP_CANONICAL_EVENTS_ENABLED: True
  ✓ Publisher canônico inicializável

[WEBHOOK] Endpoints de Webhook
----------------------------------------------------------------------
  ✓ 3 endpoint(s) de webhook encontrado(s):
    - api/v1/whatsapp/events/
    - api/whatsapp/webhook/
    - webhooks/evolution/<instance_id>/messages
  ℹ Nota: Apenas validação local. Não faz chamadas externas.

[DATABASE] Tabelas de Banco de Dados
----------------------------------------------------------------------
  ✓ WhatsAppEventLog: Existe (42 eventos nas últimas 24h)
  ✓ WhatsAppConversation: Existe (15 conversa(s))
  ✓ CanonicalEventLog: Existe (38 eventos nas últimas 24h)
  ✓ SimulatedMessage: Existe (127 mensagem(ns) simulada(s))

[SIMULATOR] Simulador de Mensagens
----------------------------------------------------------------------
  ✓ WHATSAPP_SIM_ENABLED: True
  ✓ 127 mensagem(ns) simulada(s) no banco

======================================================================
RESUMO
======================================================================

✓ OK: 8
⚠ WARN: 1
✗ FAIL: 0

Avisos:
  ⚠ Nenhum shopper habilitado

Recomendações:
  → Defina WHATSAPP_ENABLED_SHOPPERS para habilitar shoppers específicos

✓ Diagnóstico concluído — nenhuma ação executada
```

## 🐛 Troubleshooting

### Erro: "WhatsApp Gateway não disponível"

**Causa:** Módulo `core.services.whatsapp` não está instalado ou não está no `INSTALLED_APPS`.

**Solução:** Verifique se o módulo está instalado e adicionado ao `INSTALLED_APPS`.

### Erro: "Tabela não existe"

**Causa:** Migrations não foram executadas.

**Solução:** Execute migrations:
```bash
python manage.py migrate
```

### Erro: "Provider não saudável"

**Causa:** Provider não está respondendo ao healthcheck.

**Solução:** Verifique:
- Se o provider está configurado corretamente
- Se as variáveis de ambiente estão definidas
- Se o serviço do provider está rodando

## 📝 Notas

- O comando é **100% seguro** - não altera nada no sistema
- Pode ser executado em qualquer ambiente (dev, staging, produção)
- Não faz chamadas externas (exceto healthcheck do provider)
- Não expõe informações sensíveis

## 🔗 Referências

- [WhatsApp Gateway README](../../core/services/whatsapp/README.md)
- [WhatsApp Events README](../../app_whatsapp_events/README.md)
- [Canonical Events README](../../core/services/whatsapp/canonical/README.md)
