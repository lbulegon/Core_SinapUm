# 📦 Resumo dos Repositórios GitHub

## ✅ Repositórios Configurados

### 1. **MCP_SinapUm**
- **Local:** `/root/MCP_SinapUm/`
- **GitHub:** `https://github.com/lbulegon/SinapUm.git`
- **Status:** Configurado e funcionando
- **Arquivos para commit:** ~42 arquivos

### 2. **Évora/VitrineZap**
- **Local:** `/root/evora/`
- **GitHub:** `https://github.com/lbulegon/evora.git`
- **Status:** Configurado e funcionando
- **Arquivos para commit:** ~6 arquivos (modificados + novos)

### 3. **Repositório em /root/**
- **Local:** `/root/`
- **GitHub:** Não configurado (apenas local)
- **Status:** Apenas para controle local, não deve ser commitado no GitHub
- **Arquivos ignorados:** `.cache/`, arquivos pessoais, etc.

---

## 🚀 Como Fazer Commit em Cada Repositório

### MCP_SinapUm

```bash
cd /root/MCP_SinapUm

# Ver mudanças
git status

# Adicionar arquivos
git add .

# Verificar o que será commitado
git status

# Fazer commit
git commit -m "Sua mensagem de commit"

# Enviar para GitHub
git push origin main
```

### Évora/VitrineZap

```bash
cd /root/evora

# Ver mudanças
git status

# Adicionar arquivos
git add .

# Verificar o que será commitado
git status

# Fazer commit
git commit -m "Sua mensagem de commit"

# Enviar para GitHub
git push origin main
```

---

## 📋 Checklist Antes de Commitar

### ✅ Sempre verificar:

1. **Quantidade de arquivos:**
   ```bash
   git status --short | wc -l
   ```
   - Se aparecer mais de 100 arquivos, verificar o que está sendo adicionado

2. **Arquivos ignorados estão funcionando:**
   ```bash
   git check-ignore .cache/ services/*/pg_data/
   ```
   - Deve retornar os caminhos (significa que estão sendo ignorados)

3. **Ver o que será commitado:**
   ```bash
   git status
   git diff --cached --stat  # Se já adicionou arquivos
   ```

---

## 🔧 Comandos Úteis

### Ver diferenças entre repositórios locais e remotos

```bash
# MCP_SinapUm
cd /root/MCP_SinapUm
git fetch origin
git status

# Évora
cd /root/evora
git fetch origin
git status
```

### Ver histórico de commits

```bash
# MCP_SinapUm
cd /root/MCP_SinapUm
git log --oneline -10

# Évora
cd /root/evora
git log --oneline -10
```

### Ver branches

```bash
# MCP_SinapUm
cd /root/MCP_SinapUm
git branch -a

# Évora
cd /root/evora
git branch -a
```

---

## ⚠️ Importante

- **Nunca fazer commit do repositório em `/root/`** - Ele é apenas para controle local
- **Sempre verificar `git status` antes de `git add .`**
- **Cada projeto tem seu próprio `.gitignore`** - Não misturar configurações
- **Arquivos de cache e dados de runtime** devem estar sempre ignorados

---

## 📊 Status Atual

### MCP_SinapUm
- ✅ `.gitignore` configurado
- ✅ Cache e dados de runtime ignorados
- ✅ ~42 arquivos prontos para commit

### Évora
- ✅ `.gitignore` configurado
- ✅ Migrations e testes criados
- ✅ ~6 arquivos modificados/novos

---

**Última atualização:** 21/12/2025

