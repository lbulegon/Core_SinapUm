# Documentação de Inventário e Arquitetura

## 📚 Documentos Disponíveis

### 1. `existing_apps.md`
Lista completa de apps Django existentes no Core_SinapUm e Évora/VitrineZap.

**Use quando:** Precisar saber quais apps já existem antes de criar novos.

---

### 2. `existing_endpoints.md`
Mapeamento completo de endpoints e URLs relacionados a WhatsApp/Evolution.

**Use quando:** Precisar saber quais endpoints já existem antes de criar novos.

---

### 3. `risk_points.md`
Pontos de risco onde mudanças podem quebrar o sistema.

**Use quando:** For modificar código existente (⚠️ ler ANTES de modificar).

---

### 4. `ARCHITECTURE_MAPPING.md` ⭐ **IMPORTANTE**
Mapeamento claro de **o que é ANTIGO vs NOVO**.

**Use quando:**
- Estiver confuso sobre qual código usar
- Precisar saber se um arquivo é antigo ou novo
- Quiser evitar duplicação e confusão

**Conteúdo:**
- Tabela de arquivos antigos vs novos
- Mapeamento de endpoints antigos vs novos
- Mapeamento de models antigos vs novos
- Convenções de nomenclatura
- Feature flags

---

### 5. `DEPRECATION_PLAN.md`
Plano futuro de deprecação do código antigo.

**Use quando:** Quiser entender como eventualmente remover código antigo (futuro).

---

## 🛠️ Ferramentas

### Script de Verificação
```bash
# Verificar um arquivo específico
python scripts/check_architecture.py --file app_whatsapp_gateway/views.py

# Verificar se um import é antigo ou novo
python scripts/check_architecture.py --import app_whatsapp_integration

# Verificar todos os arquivos
python scripts/check_architecture.py --all
```

---

## 🎯 Regras de Ouro

### ✅ FAZER
1. **Sempre consultar** `ARCHITECTURE_MAPPING.md` antes de criar código novo
2. **Usar prefixos claros**: `app_whatsapp_gateway` (novo) vs `app_whatsapp_integration` (antigo)
3. **Adicionar comentários** `# ARQUITETURA NOVA` no topo de arquivos novos
4. **Usar feature flags** para ativação gradual
5. **Rodar script de verificação** antes de commitar

### ❌ NÃO FAZER
1. **NÃO modificar** código com prefixo `app_whatsapp_integration` (antigo)
2. **NÃO modificar** `app_sinapum.views_evolution` (antigo)
3. **NÃO usar** URLs `/api/whatsapp/*` ou `/whatsapp/api/*` (antigo)
4. **NÃO remover** código antigo sem migração completa
5. **NÃO misturar** código antigo e novo no mesmo arquivo

---

## 📖 Como Usar Esta Documentação

### Cenário 1: Criar Novo Endpoint
1. Consultar `existing_endpoints.md` para ver se já existe
2. Consultar `ARCHITECTURE_MAPPING.md` para ver padrão de URLs novo
3. Criar endpoint seguindo convenções novas
4. Adicionar feature flag se necessário

### Cenário 2: Modificar Código Existente
1. **OBRIGATÓRIO**: Ler `risk_points.md` primeiro
2. Verificar se código é antigo ou novo em `ARCHITECTURE_MAPPING.md`
3. Se for antigo: **NÃO MODIFICAR** - criar novo em vez disso
4. Se for novo: modificar com cuidado

### Cenário 3: Está Confuso?
1. Consultar `ARCHITECTURE_MAPPING.md` - tem tabela clara antigo vs novo
2. Rodar script: `python scripts/check_architecture.py --file <arquivo>`
3. Verificar comentários no código (deve ter `# ARQUITETURA NOVA` ou similar)

---

## 🔄 Atualização

Esta documentação deve ser atualizada sempre que:
- Novo app for criado
- Novo endpoint for criado
- Código antigo for deprecado
- Arquitetura mudar

**Mantido por:** Equipe de Desenvolvimento  
**Última atualização:** 2026-01-03

