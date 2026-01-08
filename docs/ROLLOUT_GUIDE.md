# Guia de Rollout Gradual - Feature Flags

## 📋 Visão Geral

Este guia descreve como fazer rollout gradual e seguro das novas funcionalidades WhatsApp usando o sistema de feature flags.

**Regra máxima:** NUNCA quebrar o sistema existente. Toda ativação deve permitir rollback instantâneo.

## 🏗️ Arquitetura

### Componentes

1. **Rollout Manager** (`core/services/feature_flags/rollout.py`)
   - Lógica de decisão (allowlist, denylist, percent)
   - Função `is_enabled()` canônica

2. **Storage** (`core/services/feature_flags/storage.py`)
   - Suporte a DB (FeatureFlagConfig model)
   - Fallback para env vars

3. **Observability** (`core/services/feature_flags/observability.py`)
   - Métricas e logs estruturados
   - Medição de latência

4. **Admin** (`core/services/feature_flags/admin.py`)
   - Interface Django Admin para gerenciar flags

## 🚩 Feature Flags Disponíveis

### WhatsApp Canonical Events
- `WHATSAPP_CANONICAL_EVENTS_ENABLED` - Habilita eventos canônicos
- `WHATSAPP_CANONICAL_SHADOW_MODE` - Modo shadow (não interfere)

### WhatsApp Routing
- `WHATSAPP_ROUTING_ENABLED` - Habilita roteamento

### WhatsApp Gateway
- `WHATSAPP_GATEWAY_ENABLED` - Habilita novo gateway

### Dual Run
- `WHATSAPP_DUAL_RUN` - Executa legado + novo para comparação

## 📊 Estratégia de Rollout

### Precedência de Decisão

1. **Denylist** (maior precedência)
   - Se `shopper_id` está na denylist → **FALSE**

2. **Allowlist**
   - Se há allowlist e `shopper_id` está nela → **TRUE**
   - Se há allowlist mas `shopper_id` não está → **FALSE**

3. **Percent Rollout**
   - Hash determinístico do `shopper_id`
   - Se hash % 100 < percent → **TRUE**

4. **Global Enabled**
   - Se flag globalmente habilitada → **TRUE**

5. **Default**
   - Valor padrão (geralmente **FALSE**)

## 🚀 Fases de Rollout

### Fase 0: DEV

**Objetivo:** Testar em ambiente de desenvolvimento

```bash
# Variáveis de ambiente
WHATSAPP_CANONICAL_SHADOW_MODE=true
WHATSAPP_CANONICAL_EVENTS_ENABLED=false
WHATSAPP_PROVIDER=simulated
WHATSAPP_DUAL_RUN=false
```

**Validação:**
- ✅ Sistema funciona normalmente
- ✅ Nenhum evento canônico gerado
- ✅ Logs mostram shadow mode desabilitado

### Fase 1: STAGING

**Objetivo:** Ativar shadow mode e dual-run com 1 shopper de teste

```bash
# Variáveis de ambiente
WHATSAPP_CANONICAL_SHADOW_MODE=true
WHATSAPP_CANONICAL_EVENTS_ENABLED=true
WHATSAPP_CANONICAL_EVENTS_ENABLED_ALLOWLIST=shopper_test_001
WHATSAPP_DUAL_RUN=true
```

**OU via DB (Django Admin):**
```python
FeatureFlagConfig.objects.create(
    name='WHATSAPP_CANONICAL_EVENTS_ENABLED',
    enabled=True,
    shadow_mode=True,
    allowlist=['shopper_test_001'],
    percent_rollout=0,
    active=True
)
```

**Validação:**
- ✅ Shadow mode ativo (eventos gerados mas não processados)
- ✅ Dual-run ativo (legado + novo executam)
- ✅ Apenas `shopper_test_001` gera eventos
- ✅ Logs mostram comparação legado vs novo
- ✅ Nenhuma divergência crítica

### Fase 2: PROD Canary (1-3 Shoppers)

**Objetivo:** Testar em produção com poucos shoppers

```bash
# Variáveis de ambiente
WHATSAPP_CANONICAL_SHADOW_MODE=true
WHATSAPP_CANONICAL_EVENTS_ENABLED=true
WHATSAPP_CANONICAL_EVENTS_ENABLED_ALLOWLIST=shopper_001,shopper_002,shopper_003
WHATSAPP_DUAL_RUN=true
```

**Monitoramento (24-48h):**
- ✅ Taxa de erro < 0.1%
- ✅ Latência p95 < 100ms adicional
- ✅ Nenhuma divergência crítica
- ✅ Logs estruturados funcionando

**Rollback:**
```bash
# Desabilitar imediatamente
WHATSAPP_CANONICAL_EVENTS_ENABLED=false
# OU remover da allowlist
WHATSAPP_CANONICAL_EVENTS_ENABLED_ALLOWLIST=
```

### Fase 3: PROD Percent Rollout

**Objetivo:** Expandir gradualmente para mais shoppers

#### 3.1: 5%
```bash
WHATSAPP_CANONICAL_SHADOW_MODE=true
WHATSAPP_CANONICAL_EVENTS_ENABLED=true
WHATSAPP_CANONICAL_EVENTS_ENABLED_PERCENT=5
WHATSAPP_DUAL_RUN=true
```

**Monitorar:** 24h

#### 3.2: 10%
```bash
WHATSAPP_CANONICAL_EVENTS_ENABLED_PERCENT=10
```

**Monitorar:** 24h

#### 3.3: 25%
```bash
WHATSAPP_CANONICAL_EVENTS_ENABLED_PERCENT=25
```

**Monitorar:** 48h

#### 3.4: 50%
```bash
WHATSAPP_CANONICAL_EVENTS_ENABLED_PERCENT=50
```

**Monitorar:** 48h

#### 3.5: 100%
```bash
WHATSAPP_CANONICAL_EVENTS_ENABLED_PERCENT=100
```

**Monitorar:** 7 dias

### Fase 4: Cutover

**Objetivo:** Desligar dual-run e shadow mode quando estável

```bash
WHATSAPP_CANONICAL_SHADOW_MODE=false
WHATSAPP_DUAL_RUN=false
WHATSAPP_CANONICAL_EVENTS_ENABLED=true
WHATSAPP_CANONICAL_EVENTS_ENABLED_PERCENT=100
```

**Manter flags ativas por 30 dias** para rollback rápido se necessário.

## 🔧 Configuração

### Via Environment Variables

```bash
# Flag básica
WHATSAPP_CANONICAL_EVENTS_ENABLED=true

# Shadow mode
WHATSAPP_CANONICAL_SHADOW_MODE=true

# Allowlist (separado por vírgula)
WHATSAPP_CANONICAL_EVENTS_ENABLED_ALLOWLIST=shopper_001,shopper_002

# Denylist (separado por vírgula)
WHATSAPP_CANONICAL_EVENTS_ENABLED_DENYLIST=shopper_bad_001

# Percent rollout (0-100)
WHATSAPP_CANONICAL_EVENTS_ENABLED_PERCENT=25

# Dual run
WHATSAPP_DUAL_RUN=true
```

### Via Django Admin

1. Acessar `/admin/`
2. Ir em **Feature Flag Configs**
3. Criar/editar flag
4. Configurar:
   - `enabled`: True/False
   - `shadow_mode`: True/False
   - `allowlist`: JSON array `["shopper_001", "shopper_002"]`
   - `denylist`: JSON array `["shopper_bad_001"]`
   - `percent_rollout`: 0-100

### Via API (Futuro)

```python
# POST /api/internal/flags/update
{
    "name": "WHATSAPP_CANONICAL_EVENTS_ENABLED",
    "enabled": true,
    "shadow_mode": true,
    "allowlist": ["shopper_001"],
    "percent_rollout": 0
}
```

## 📊 Observabilidade

### Métricas Disponíveis

- `canonical_events_published_count` - Eventos publicados
- `canonical_publish_fail_count` - Falhas na publicação
- `routing_assignments_count` - Atribuições de roteamento
- `divergence_count` - Divergências (dual-run)
- `latency_ms` - Latência em milissegundos

### Logs Estruturados

```json
{
    "event": "feature_flag_check",
    "flag_name": "WHATSAPP_CANONICAL_EVENTS_ENABLED",
    "enabled": true,
    "shopper_id": "shopper_001",
    "reason": "allowlist",
    "timestamp": "2026-01-07T12:00:00Z"
}
```

### Verificação

```bash
# Ver logs de feature flags
docker logs mcp_sinapum_web | grep FEATURE_FLAG

# Ver logs de eventos canônicos
docker logs mcp_sinapum_web | grep CANONICAL_EVENT

# Ver divergências (dual-run)
docker logs mcp_sinapum_web | grep DUAL_RUN
```

## 🔄 Rollback

### Rollback Imediato (Global)

```bash
# Desabilitar flag globalmente
WHATSAPP_CANONICAL_EVENTS_ENABLED=false
```

### Rollback por Shopper

```bash
# Adicionar à denylist
WHATSAPP_CANONICAL_EVENTS_ENABLED_DENYLIST=shopper_problematico
```

### Rollback Percentual

```bash
# Reduzir percentual
WHATSAPP_CANONICAL_EVENTS_ENABLED_PERCENT=0
```

## ✅ Checklist de Validação

### Antes de Ativar

- [ ] Código testado em DEV
- [ ] Shadow mode testado
- [ ] Dual-run testado
- [ ] Logs estruturados funcionando
- [ ] Métricas configuradas
- [ ] Plano de rollback definido

### Durante Rollout

- [ ] Monitorar taxa de erro
- [ ] Monitorar latência
- [ ] Verificar divergências (dual-run)
- [ ] Validar logs estruturados
- [ ] Confirmar que legado continua funcionando

### Após Cutover

- [ ] Validar que novo pipeline está funcionando
- [ ] Confirmar que legado pode ser desligado
- [ ] Manter flags ativas por 30 dias
- [ ] Documentar lições aprendidas

## 🚨 Troubleshooting

### Flag não está funcionando

1. Verificar se flag está no DB ou env vars
2. Verificar precedência (denylist > allowlist > percent)
3. Verificar logs: `grep FEATURE_FLAG`

### Divergências no dual-run

1. Verificar logs de divergência
2. Comparar resultados legado vs novo
3. Identificar causa raiz
4. Corrigir ou fazer rollback

### Latência alta

1. Verificar métricas de latência
2. Identificar gargalo (normalizer, publisher, etc.)
3. Otimizar ou fazer rollback

## 📝 Notas Importantes

- **Nunca ativar em produção sem testar em staging**
- **Sempre manter dual-run ativo inicialmente**
- **Monitorar por pelo menos 24h antes de aumentar percentual**
- **Manter flags ativas por 30 dias após cutover**
- **Documentar todas as mudanças de flag**
