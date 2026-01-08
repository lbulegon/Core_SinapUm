# Checklist de Rollout Seguro - Eventos Canônicos WhatsApp v1.0

Checklist completo para rollout seguro e incremental do sistema de eventos canônicos.

## 🎯 Fase 0: Desenvolvimento (Shadow Mode)

### Configuração
- [ ] `WHATSAPP_CANONICAL_EVENTS_ENABLED=true`
- [ ] `WHATSAPP_CANONICAL_SHADOW_MODE=true`
- [ ] `WHATSAPP_ROUTING_ENABLED=false`
- [ ] `WHATSAPP_GROUP_ROUTING_ENABLED=false`

### Testes
- [ ] Testar normalização de eventos Evolution
- [ ] Testar normalização de eventos Cloud API
- [ ] Testar normalização de eventos Baileys
- [ ] Testar normalização de eventos Simulated
- [ ] Verificar logs de eventos gerados (sem persistir)
- [ ] Validar que webhooks existentes continuam funcionando

### Validações
- [ ] Nenhum evento é persistido no banco
- [ ] Nenhum signal é emitido
- [ ] Webhooks existentes não são afetados
- [ ] Logs mostram eventos sendo normalizados

## 🧪 Fase 1: Staging (Shadow + Logs Comparativos)

### Configuração
- [ ] `WHATSAPP_CANONICAL_EVENTS_ENABLED=true`
- [ ] `WHATSAPP_CANONICAL_SHADOW_MODE=true`
- [ ] `WHATSAPP_ROUTING_ENABLED=false`
- [ ] Logs comparativos habilitados

### Testes
- [ ] Comparar eventos normalizados com payloads brutos
- [ ] Validar idempotência (enviar mesmo evento 2x)
- [ ] Testar com diferentes providers
- [ ] Monitorar performance (latência)

### Validações
- [ ] Eventos normalizados corretamente
- [ ] Idempotência funcionando
- [ ] Sem duplicação de eventos
- [ ] Latência aceitável (< 100ms)

## 🚀 Fase 2: Produção Beta (Por Shopper - Allowlist)

### Configuração
- [ ] `WHATSAPP_CANONICAL_EVENTS_ENABLED=true`
- [ ] `WHATSAPP_CANONICAL_SHADOW_MODE=false` (persistir eventos)
- [ ] `WHATSAPP_ROUTING_ENABLED=true`
- [ ] `WHATSAPP_GROUP_ROUTING_ENABLED=true`
- [ ] `WHATSAPP_ASSIGNMENT_POLICY=default`
- [ ] Allowlist de `shopper_id`s configurada

### Migrations
- [ ] Aplicar migrations do `app_whatsapp_events`
- [ ] Verificar criação das tabelas
- [ ] Validar índices criados

### Testes
- [ ] Testar com 1 shopper beta
- [ ] Validar persistência de eventos
- [ ] Validar criação de conversações
- [ ] Validar atribuição de SKM
- [ ] Testar roteamento em grupo
- [ ] Testar roteamento em private

### Monitoramento
- [ ] Taxa de eventos por minuto
- [ ] Latência de processamento
- [ ] Taxa de erros
- [ ] Duplicação de eventos
- [ ] Uso de memória/CPU

### Validações
- [ ] Eventos sendo persistidos corretamente
- [ ] Conversações sendo criadas
- [ ] SKM sendo atribuído corretamente
- [ ] Sem erros críticos
- [ ] Performance aceitável

## 🌐 Fase 3: Produção (100% - Gradual)

### Configuração
- [ ] `WHATSAPP_CANONICAL_EVENTS_ENABLED=true`
- [ ] `WHATSAPP_CANONICAL_SHADOW_MODE=false`
- [ ] `WHATSAPP_ROUTING_ENABLED=true`
- [ ] `WHATSAPP_GROUP_ROUTING_ENABLED=true`
- [ ] Remover allowlist (todos os shoppers)

### Rollout Gradual
- [ ] Dia 1: 10% dos shoppers
- [ ] Dia 2: 25% dos shoppers
- [ ] Dia 3: 50% dos shoppers
- [ ] Dia 4: 75% dos shoppers
- [ ] Dia 5: 100% dos shoppers

### Monitoramento Contínuo
- [ ] Taxa de eventos (por hora/dia)
- [ ] Latência p50, p95, p99
- [ ] Taxa de erros
- [ ] Duplicação de eventos
- [ ] Uso de recursos (CPU, memória, DB)
- [ ] Tamanho das tabelas

### Alertas
- [ ] Taxa de erros > 1%
- [ ] Latência p95 > 500ms
- [ ] Duplicação de eventos > 0.1%
- [ ] Uso de CPU > 80%
- [ ] Uso de memória > 80%
- [ ] Espaço em disco < 20%

## 🔄 Rollback

### Procedimento de Rollback
1. [ ] Desabilitar feature flags:
   ```bash
   WHATSAPP_CANONICAL_EVENTS_ENABLED=false
   WHATSAPP_ROUTING_ENABLED=false
   ```
2. [ ] Verificar que webhooks existentes continuam funcionando
3. [ ] Monitorar logs por 15 minutos
4. [ ] Validar que não há impacto no sistema

### Validações Pós-Rollback
- [ ] Webhooks existentes funcionando normalmente
- [ ] Sem erros críticos
- [ ] Performance normal
- [ ] Sem perda de dados

## 📊 Métricas de Sucesso

### KPIs
- [ ] Taxa de eventos normalizados: > 99%
- [ ] Taxa de idempotência: 100%
- [ ] Latência p95: < 200ms
- [ ] Taxa de erros: < 0.1%
- [ ] Duplicação de eventos: 0%

### Métricas de Negócio
- [ ] Conversações criadas corretamente
- [ ] SKM atribuído corretamente
- [ ] Threads resolvidos corretamente
- [ ] Eventos disponíveis para SKM Score

## 🐛 Troubleshooting

### Problemas Comuns

#### Eventos Duplicados
- [ ] Verificar `idempotency_key` sendo gerado corretamente
- [ ] Verificar constraint unique no banco
- [ ] Verificar logs de idempotência

#### Latência Alta
- [ ] Verificar índices no banco
- [ ] Verificar queries N+1
- [ ] Verificar uso de cache
- [ ] Verificar conexões de banco

#### Erros de Normalização
- [ ] Verificar payloads brutos nos logs
- [ ] Verificar normalizers por provider
- [ ] Verificar schemas Pydantic

#### Conversações Não Criadas
- [ ] Verificar `thread_key` sendo gerado corretamente
- [ ] Verificar `get_or_create_conversation()`
- [ ] Verificar logs de criação

## ✅ Checklist Final

### Antes de Produção
- [ ] Todas as migrations aplicadas
- [ ] Feature flags configuradas
- [ ] Monitoramento configurado
- [ ] Alertas configurados
- [ ] Documentação atualizada
- [ ] Equipe treinada
- [ ] Plano de rollback testado

### Durante Produção
- [ ] Monitoramento ativo
- [ ] Logs sendo revisados
- [ ] Métricas sendo coletadas
- [ ] Equipe de plantão disponível

### Pós-Produção
- [ ] Métricas analisadas
- [ ] Problemas documentados
- [ ] Melhorias identificadas
- [ ] Próximos passos definidos
