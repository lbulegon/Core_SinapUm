# Plano de Deprecação - Arquitetura Antiga

## 🎯 Objetivo
Plano claro para **eventualmente** remover código antigo sem quebrar o sistema.

---

## ⚠️ IMPORTANTE
**NÃO EXECUTAR ESTE PLANO AGORA!**  
Este é um plano para o **futuro**, quando a nova arquitetura estiver 100% estável e testada.

---

## 📅 FASES DE DEPRECAÇÃO

### Fase 0: Coexistência (ATUAL)
**Status:** ✅ Em andamento  
**Prazo:** Indefinido

- ✅ Código antigo funciona normalmente
- ✅ Código novo implementado em paralelo
- ✅ Feature flags desabilitadas por padrão
- ✅ Nenhuma modificação no código antigo

**Ação:** Nenhuma. Apenas manter funcionando.

---

### Fase 1: Marcação como Deprecated
**Status:** ⏳ Futuro  
**Prazo:** Após 3 meses de testes da nova arquitetura

**Ações:**
1. Adicionar decorator `@deprecated` em funções antigas
2. Adicionar warnings em logs quando código antigo for usado
3. Documentar em README que código antigo está deprecated
4. Criar issue no GitHub marcando código antigo para remoção futura

**Código de exemplo:**
```python
import warnings
from functools import wraps

def deprecated(reason):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            warnings.warn(
                f"{func.__name__} está deprecated. {reason}",
                DeprecationWarning,
                stacklevel=2
            )
            return func(*args, **kwargs)
        return wrapper
    return decorator

# Usar:
@deprecated("Use app_whatsapp_gateway.views.webhook_receiver instead")
def webhook_evolution_api(request):
    ...
```

---

### Fase 2: Migração Gradual
**Status:** ⏳ Futuro  
**Prazo:** Após Fase 1 (6 meses)

**Ações:**
1. Migrar shopper por shopper para nova arquitetura
2. Desabilitar código antigo por shopper migrado
3. Monitorar erros e performance
4. Documentar shoppers migrados

**Checklist por Shopper:**
- [ ] Shopper testado na nova arquitetura
- [ ] Todas as conversas migradas
- [ ] Histórico preservado
- [ ] Performance validada
- [ ] Sem erros por 1 semana
- [ ] Feature flag desabilitada para este shopper

---

### Fase 3: Desativação Completa
**Status:** ⏳ Futuro  
**Prazo:** Após 100% dos shoppers migrados

**Ações:**
1. Desabilitar feature flag globalmente
2. Redirecionar endpoints antigos para novos (com redirect 301)
3. Adicionar mensagem de erro em endpoints antigos
4. Monitorar por 1 mês se alguém ainda usa endpoints antigos

**Código de exemplo:**
```python
# Em urls.py (futuro)
if settings.FEATURE_DEPRECATE_LEGACY_WHATSAPP:
    # Redirecionar para novo endpoint
    path('api/whatsapp/webhook/evolution/', 
         redirect_to_new_webhook, 
         name='legacy_webhook_redirect'),
else:
    # Manter antigo
    path('api/whatsapp/webhook/evolution/', 
         webhook_evolution_api, 
         name='webhook_evolution_api'),
```

---

### Fase 4: Remoção (ÚLTIMA FASE)
**Status:** ⏳ Futuro  
**Prazo:** Após 3 meses sem uso do código antigo

**⚠️ ATENÇÃO:** Só executar se:
- ✅ 100% dos shoppers migrados
- ✅ 0 acessos aos endpoints antigos por 3 meses
- ✅ Backup completo do código antigo
- ✅ Documentação atualizada

**Ações:**
1. Criar branch `deprecate-legacy-whatsapp`
2. Remover arquivos antigos:
   - `app_whatsapp_integration/` (Évora) - **CUIDADO: Verificar se não há dependências**
   - `app_sinapum/views_evolution.py` (Core) - **CUIDADO: Verificar se não há dependências**
   - `app_sinapum/evolution_service.py` (Core) - **CUIDADO: Verificar se não há dependências**
3. Remover URLs antigas
4. Remover models antigos (após migração de dados)
5. Atualizar documentação
6. Testar tudo
7. Merge para main

**Arquivos a Remover (FUTURO):**
```
Source/evora/app_whatsapp_integration/
  - models.py (após migração de dados)
  - views.py
  - evolution_service.py
  - urls.py

Core_SinapUm/app_sinapum/
  - views_evolution.py
  - evolution_service.py (se não usado por outros módulos)
```

---

## 📊 MÉTRICAS DE MONITORAMENTO

### Métricas para Decidir Deprecação

1. **Uso de Endpoints Antigos**
   - Quantidade de requests por dia
   - Último acesso
   - Shoppers usando

2. **Performance**
   - Tempo de resposta (antigo vs novo)
   - Taxa de erro
   - Throughput

3. **Funcionalidades**
   - Features cobertas pela nova arquitetura
   - Features faltando na nova arquitetura

---

## 🚫 O QUE NÃO FAZER

- ❌ **NÃO remover código antigo** sem migração completa
- ❌ **NÃO modificar código antigo** sem feature flag
- ❌ **NÃO forçar migração** sem teste adequado
- ❌ **NÃO remover models** sem migração de dados
- ❌ **NÃO remover endpoints** sem redirecionamento

---

## ✅ CHECKLIST ANTES DE DEPRECAR

Antes de marcar qualquer código como deprecated:

- [ ] Nova arquitetura 100% funcional
- [ ] Todos os testes passando
- [ ] Documentação completa
- [ ] Feature flags implementadas
- [ ] Plano de migração definido
- [ ] Aprovação da equipe
- [ ] Backup completo

---

## 📝 NOTAS

- Este plano é **conservador** - prioriza segurança sobre velocidade
- Cada fase deve ter **aprovação explícita** antes de avançar
- **Sempre manter backup** do código antigo (mesmo após remoção)
- **Documentar tudo** - decisões, métricas, problemas encontrados

---

**Última atualização:** 2026-01-03  
**Status:** Plano futuro - não executar agora

