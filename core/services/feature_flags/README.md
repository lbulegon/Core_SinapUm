# Feature Flags & Rollout Manager

Sistema completo de feature flags com rollout gradual e seguro para ativação incremental de funcionalidades.

## 📋 Características

- ✅ **Rollout Gradual**: Allowlist, denylist, percentual
- ✅ **Shadow Mode**: Executa sem interferir no fluxo
- ✅ **Dual-Run**: Compara legado vs novo pipeline
- ✅ **Storage Flexível**: DB (FeatureFlagConfig) + fallback env vars
- ✅ **Observabilidade**: Métricas e logs estruturados
- ✅ **Rollback Instantâneo**: Desligar flags sem deploy
- ✅ **Zero Breaking Changes**: Não altera comportamento existente

## 🚀 Uso Rápido

### Verificar se Flag Está Habilitada

```python
from core.services.feature_flags.rollout import is_enabled

# Verificação global
if is_enabled('WHATSAPP_CANONICAL_EVENTS_ENABLED'):
    # Executar novo código
    pass

# Verificação por shopper
shopper_id = "shopper_123"
if is_enabled('WHATSAPP_CANONICAL_EVENTS_ENABLED', shopper_id=shopper_id):
    # Executar novo código para este shopper
    pass
```

### Configurar via Environment Variables

```bash
# Habilitar globalmente
WHATSAPP_CANONICAL_EVENTS_ENABLED=true

# Shadow mode
WHATSAPP_CANONICAL_SHADOW_MODE=true

# Allowlist
WHATSAPP_CANONICAL_EVENTS_ENABLED_ALLOWLIST=shopper_001,shopper_002

# Denylist
WHATSAPP_CANONICAL_EVENTS_ENABLED_DENYLIST=shopper_bad_001

# Percent rollout
WHATSAPP_CANONICAL_EVENTS_ENABLED_PERCENT=25
```

### Configurar via Django Admin

1. Acessar `/admin/core/services/featureflagconfig/`
2. Criar/editar flag
3. Configurar allowlist, denylist, percent_rollout
4. Salvar (cache é limpo automaticamente)

## 📊 Precedência de Decisão

1. **Denylist** (maior precedência) → `FALSE`
2. **Allowlist** → `TRUE` se está na lista, `FALSE` caso contrário
3. **Percent Rollout** → Hash determinístico do `shopper_id`
4. **Global Enabled** → `TRUE`/`FALSE`
5. **Default** → Valor padrão

## 🔧 Estrutura

```
core/services/feature_flags/
├── __init__.py          # Exports principais
├── rollout.py           # Lógica de decisão
├── settings.py          # Definição de flags
├── storage.py           # Armazenamento (DB + env)
├── models.py            # Model FeatureFlagConfig
├── admin.py             # Django Admin
├── observability.py     # Métricas e logs
├── examples.py          # Exemplos de uso
└── README.md            # Esta documentação
```

## 📚 Documentação Completa

- **[ROLLOUT_GUIDE.md](../../../docs/ROLLOUT_GUIDE.md)** - Guia completo de rollout passo-a-passo
- **[ROLLOUT_CONFIG_EXAMPLE.env](ROLLOUT_CONFIG_EXAMPLE.env)** - Exemplos de configuração

## ✅ Garantias

- **Nunca quebra**: Se flags OFF, comportamento existente é mantido
- **Rollback instantâneo**: Desligar flag e sistema volta ao normal
- **Zero downtime**: Mudanças via DB não requerem deploy
- **Observável**: Logs e métricas estruturados
