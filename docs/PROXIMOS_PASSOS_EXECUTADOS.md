# Próximos Passos Executados

**Data:** 2026-01-08  
**Status:** ✅ CONCLUÍDO

## 📋 Passos Executados

### 1. ✅ Criar Flags via Django Admin/Código

**Executado:**
```bash
docker exec mcp_sinapum_web python manage.py shell --command="from core.services.feature_flags.models import FeatureFlagConfig; ..."
```

**Resultado:**
- ✓ 2 flags criadas no banco de dados:
  - `WHATSAPP_CANONICAL_EVENTS_ENABLED`: enabled=True, shadow_mode=True
  - `WHATSAPP_ROUTING_ENABLED`: enabled=False, shadow_mode=False

**Verificação:**
```bash
docker exec mcp_sinapum_web python manage.py shell --command="from core.services.feature_flags.models import FeatureFlagConfig; print(FeatureFlagConfig.objects.count())"
```

**Resultado:** `Flags no DB: 2` ✅

---

### 2. ✅ Integrar WebhookCompatLayer no Endpoint inbound_webhook

**Arquivo modificado:** `app_whatsapp/api/views.py`

**Alterações:**
- Integrado `WebhookCompatLayer` no endpoint `inbound_webhook`
- Adicionado fallback seguro se compat layer falhar
- Wrapper do handler original para gerar eventos canônicos

**Código adicionado:**
```python
# Integrar WebhookCompatLayer para gerar eventos canônicos
try:
    from core.services.whatsapp.canonical.compat import get_webhook_compat_layer
    compat_layer = get_webhook_compat_layer()
    
    # Wrapper do handler original para gerar eventos canônicos
    original_handler = lambda req, *args, **kwargs: provider.handle_inbound_webhook(req)
    wrapped_handler = compat_layer.wrap_webhook_handler(
        original_handler,
        provider=provider.name,
        instance_key=request.data.get('instance_key') if hasattr(request, 'data') else None
    )
    
    result = wrapped_handler(request)
except Exception as e:
    # Fallback: executar handler original se compat layer falhar
    import logging
    logger = logging.getLogger(__name__)
    logger.warning(f"Erro ao usar WebhookCompatLayer: {e}, usando handler original")
    result = provider.handle_inbound_webhook(request)
```

**Status:** ✅ Integrado com fallback seguro

---

### 3. ✅ Criar Script de Monitoramento de Logs

**Arquivo criado:** `scripts/monitor_shadow_logs.sh`

**Funcionalidades:**
- Monitora logs em tempo real
- Filtra logs de SHADOW MODE e FEATURE_FLAG
- Mostra eventos canônicos e webhooks
- Interface colorida e legível

**Uso:**
```bash
./scripts/monitor_shadow_logs.sh
```

**Ou manualmente:**
```bash
docker logs -f mcp_sinapum_web 2>&1 | grep --line-buffered -E "\[SHADOW MODE\]|\[FEATURE_FLAG\]|canonical|webhook" --color=always
```

**Status:** ✅ Script criado e pronto para uso

---

## 🎯 Próximos Passos Recomendados

### 1. Testar com Webhook Real

**Opção A: Simular Webhook (se provider=simulated)**
```bash
curl -X POST http://localhost:5000/api/whatsapp/instances/test_instance/simulate/inbound/ \
  -H "Content-Type: application/json" \
  -d '{
    "from_number": "+5511999999999",
    "text": "Teste de mensagem",
    "shopper_id": "test_shopper_001"
  }'
```

**Opção B: Enviar Webhook Real**
- Configurar webhook no provider (Evolution, Cloud, etc.)
- Enviar mensagem de teste
- Monitorar logs em tempo real

**Monitoramento:**
```bash
./scripts/monitor_shadow_logs.sh
```

**Logs esperados:**
```
[FEATURE_FLAG] WHATSAPP_CANONICAL_EVENTS_ENABLED=True (reason: global_enabled)
[SHADOW MODE] Evento canônico gerado (não persistido): message from +5511999999999
```

---

### 2. Validar Shadow Mode

**Verificar:**
- Eventos são gerados mas não persistidos (shadow mode)
- Logs mostram "[SHADOW MODE] Evento canônico gerado"
- Fluxo legado continua funcionando normalmente

**Comando:**
```bash
docker logs mcp_sinapum_web --tail 100 | grep -E "SHADOW|FEATURE_FLAG"
```

---

### 3. Configurar Allowlist (Fase 1 - STAGING)

**Via Django Admin:**
1. Acessar `/admin/core/services/featureflagconfig/`
2. Editar flag `WHATSAPP_CANONICAL_EVENTS_ENABLED`
3. Adicionar shopper de teste em `allowlist`: `["shopper_test_001"]`
4. Salvar

**Via código:**
```python
from core.services.feature_flags.models import FeatureFlagConfig

flag = FeatureFlagConfig.objects.get(name='WHATSAPP_CANONICAL_EVENTS_ENABLED')
flag.allowlist = ['shopper_test_001']
flag.save()
```

**Via env vars:**
```bash
WHATSAPP_CANONICAL_EVENTS_ENABLED_ALLOWLIST=shopper_test_001
```

---

### 4. Ativar Dual-Run

**Para comparar legado vs novo:**

**Via env vars:**
```bash
WHATSAPP_DUAL_RUN=true
```

**Via Django Admin:**
1. Criar flag `WHATSAPP_DUAL_RUN` se não existir
2. `enabled`: True
3. `shadow_mode`: False

**Logs esperados:**
```
[DUAL RUN] Executando legado + novo pipeline
[DUAL RUN] Comparando resultados...
[DUAL RUN] Divergências detectadas: 0
```

---

## 📊 Status Atual

### Sistema Configurado:
- ✅ Feature Flags criadas no DB
- ✅ WebhookCompatLayer integrado
- ✅ Script de monitoramento criado
- ✅ Shadow mode ativo
- ✅ Canonical events habilitados

### Pronto para Testar:
- ⏳ Webhook de teste (simulado ou real)
- ⏳ Validação de logs de SHADOW MODE
- ⏳ Configuração de allowlist (Fase 1)

---

## 🔍 Verificações Rápidas

### Verificar Flags no DB:
```bash
docker exec mcp_sinapum_web python manage.py shell --command="from core.services.feature_flags.models import FeatureFlagConfig; [print(f'{f.name}: enabled={f.enabled}, shadow={f.shadow_mode}') for f in FeatureFlagConfig.objects.all()]"
```

### Verificar Configuração via Env Vars:
```bash
docker exec mcp_sinapum_web env | grep WHATSAPP_CANONICAL
```

### Verificar Logs Recentes:
```bash
docker logs mcp_sinapum_web --tail 50 | grep -E "SHADOW|FEATURE_FLAG"
```

### Monitorar em Tempo Real:
```bash
./scripts/monitor_shadow_logs.sh
```

---

## 📚 Referências

- [ROLLOUT_GUIDE.md](ROLLOUT_GUIDE.md) - Guia completo de rollout
- [VALIDACAO_SISTEMA.md](VALIDACAO_SISTEMA.md) - Resultados dos testes
- [PROXIMOS_PASSOS_ROLLOUT.md](PROXIMOS_PASSOS_ROLLOUT.md) - Próximos passos detalhados
