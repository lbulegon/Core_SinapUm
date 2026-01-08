# Próximos Passos - Rollout Manager

## 📋 Status Atual

### ✅ Implementado
- [x] Módulo completo de Feature Flags & Rollout Manager
- [x] Integração com WebhookCompatLayer
- [x] Integração com WhatsAppRouter
- [x] Model FeatureFlagConfig
- [x] Django Admin
- [x] Observabilidade (métricas e logs)
- [x] Documentação completa (ROLLOUT_GUIDE.md)
- [x] Commits realizados e enviados

### ⏳ Próximos Passos

## 1. Criar Migrations (OBRIGATÓRIO)

O model `FeatureFlagConfig` precisa de migrations para criar a tabela no banco.

```bash
# No container
docker exec mcp_sinapum_web python manage.py makemigrations core.services.feature_flags

# Verificar migrations criadas
docker exec mcp_sinapum_web python manage.py makemigrations core.services.feature_flags --dry-run

# Aplicar migrations
docker exec mcp_sinapum_web python manage.py migrate core.services.feature_flags
```

**Importante:** Sem migrations, o sistema funcionará apenas com env vars (fallback).

---

## 2. Testar em Desenvolvimento (Fase 0)

### 2.1 Validar que Sistema Funciona

```bash
# Verificar que não quebrou nada
docker exec mcp_sinapum_web python manage.py whatsapp_diagnose --skip-checks

# Verificar imports
docker exec mcp_sinapum_web python -c "from core.services.feature_flags.rollout import is_enabled; print('OK')"
```

### 2.2 Testar Feature Flags OFF (Estado Seguro)

**Garantir que com flags OFF, nada muda:**

```bash
# Configurar variáveis (flags desligadas)
WHATSAPP_CANONICAL_EVENTS_ENABLED=false
WHATSAPP_ROUTING_ENABLED=false

# Reiniciar container
docker compose restart web

# Validar que sistema funciona normalmente
# - Webhooks continuam funcionando
# - Nenhum evento canônico gerado
# - Logs não mostram erros
```

---

## 3. Configurar Flags Iniciais (Fase 0)

### 3.1 Via Environment Variables (Simples)

Editar `docker-compose.yml` ou criar `.env`:

```bash
# Fase 0: DEV - Shadow mode apenas
WHATSAPP_CANONICAL_SHADOW_MODE=true
WHATSAPP_CANONICAL_EVENTS_ENABLED=false
WHATSAPP_ROUTING_ENABLED=false
WHATSAPP_DUAL_RUN=false
```

### 3.2 Via Django Admin (Após Migrations)

1. Acessar `/admin/`
2. Ir em **Feature Flag Configs**
3. Criar flag `WHATSAPP_CANONICAL_EVENTS_ENABLED`:
   - `enabled`: False
   - `shadow_mode`: True
   - `allowlist`: `[]`
   - `denylist`: `[]`
   - `percent_rollout`: 0

---

## 4. Ativar Shadow Mode (Fase 0 → Fase 1)

### 4.1 Ativar Shadow Mode Globalmente

```bash
# Via env vars
WHATSAPP_CANONICAL_SHADOW_MODE=true
WHATSAPP_CANONICAL_EVENTS_ENABLED=true

# Reiniciar container
docker compose restart web
```

### 4.2 Verificar que Shadow Mode Está Funcionando

```bash
# Verificar logs
docker logs mcp_sinapum_web | grep "SHADOW MODE"

# Deve mostrar mensagens como:
# [SHADOW MODE] Evento canônico gerado (não persistido)
```

**Validação:**
- ✅ Eventos são gerados mas não persistidos
- ✅ Fluxo legado continua funcionando
- ✅ Nenhum erro nos logs

---

## 5. Testar com Allowlist (Fase 1)

### 5.1 Configurar Allowlist

**Via env vars:**
```bash
WHATSAPP_CANONICAL_EVENTS_ENABLED_ALLOWLIST=shopper_test_001
```

**Via Django Admin:**
```python
config.allowlist = ["shopper_test_001"]
config.save()
```

### 5.2 Validar

```bash
# Verificar logs
docker logs mcp_sinapum_web | grep "FEATURE_FLAG" | grep "shopper_test_001"

# Deve mostrar:
# [FEATURE_FLAG] WHATSAPP_CANONICAL_EVENTS_ENABLED=true (reason: allowlist)
```

---

## 6. Implementar Dual-Run (Fase 1 → Fase 2)

### 6.1 Ativar Dual-Run

```bash
WHATSAPP_DUAL_RUN=true
```

### 6.2 Validar Comparação

O dual-run deve executar legado + novo e comparar resultados:

```bash
# Verificar logs de divergências
docker logs mcp_sinapum_web | grep "DUAL_RUN"

# Verificar que ambos os fluxos executam
docker logs mcp_sinapum_web | grep -E "legacy|canonical"
```

---

## 7. Rollout Percentual (Fase 2 → Fase 3)

### 7.1 Começar com 5%

**Via env vars:**
```bash
WHATSAPP_CANONICAL_EVENTS_ENABLED_PERCENT=5
WHATSAPP_CANONICAL_EVENTS_ENABLED_ALLOWLIST=  # Remover allowlist
```

**Via Django Admin:**
```python
config.percent_rollout = 5
config.allowlist = []
config.save()
```

### 7.2 Monitorar por 24h

- ✅ Taxa de erro < 0.1%
- ✅ Latência p95 < 100ms adicional
- ✅ Nenhuma divergência crítica

### 7.3 Aumentar Gradualmente

- 5% → 10% (24h)
- 10% → 25% (48h)
- 25% → 50% (48h)
- 50% → 100% (7 dias)

---

## 8. Criar API/Admin para Gerenciar Flags (Opcional mas Recomendado)

### 8.1 Endpoints Internos Protegidos

Criar endpoints em `core/services/feature_flags/api/`:

```python
# GET /api/internal/flags
# POST /api/internal/flags/update
# GET /api/internal/flags/{flag_name}
```

**Proteção:** Admin-only ou token interno

### 8.2 Usar Django Admin (Já Implementado)

Acessar `/admin/core/services/featureflagconfig/`

---

## 9. Configurar Observabilidade

### 9.1 Métricas Disponíveis

- `canonical_events_published_count`
- `canonical_publish_fail_count`
- `routing_assignments_count`
- `divergence_count` (dual-run)
- `latency_ms`

### 9.2 Integrar com Sistema de Métricas

Se usar Prometheus/Grafana:
- Expor métricas via endpoint `/metrics`
- Criar dashboards para monitorar rollout

---

## 10. Documentar e Treinar

### 10.1 Documentação

- [x] ROLLOUT_GUIDE.md criado
- [ ] Treinar equipe no uso do sistema
- [ ] Documentar processos de rollback

### 10.2 Runbooks

- Como fazer rollback rápido
- Como adicionar shopper à allowlist
- Como verificar métricas

---

## 📝 Checklist de Validação

### Antes de Ativar em Produção

- [ ] Migrations criadas e aplicadas
- [ ] Sistema testado em DEV com flags OFF
- [ ] Shadow mode testado e validado
- [ ] Dual-run testado em staging
- [ ] Logs estruturados funcionando
- [ ] Métricas configuradas
- [ ] Plano de rollback definido
- [ ] Equipe treinada

### Durante Rollout

- [ ] Monitorar taxa de erro (< 0.1%)
- [ ] Monitorar latência (< 100ms adicional)
- [ ] Verificar divergências (dual-run)
- [ ] Validar logs estruturados
- [ ] Confirmar que legado continua funcionando

---

## 🚨 Rollback Imediato

Se algo der errado:

```bash
# Rollback global (via env)
WHATSAPP_CANONICAL_EVENTS_ENABLED=false

# Rollback por shopper (via denylist)
WHATSAPP_CANONICAL_EVENTS_ENABLED_DENYLIST=shopper_problematico

# Reiniciar container
docker compose restart web
```

**Tempo estimado:** < 1 minuto

---

## 📚 Referências

- [ROLLOUT_GUIDE.md](ROLLOUT_GUIDE.md) - Guia completo
- [WHATSAPP_DIAGNOSTIC_COMMAND.md](WHATSAPP_DIAGNOSTIC_COMMAND.md) - Comando de diagnóstico
- [core/services/feature_flags/README.md](../core/services/feature_flags/README.md) - Documentação do módulo
