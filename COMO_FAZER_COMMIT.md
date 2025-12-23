# Como Fazer Commit no Repositório MCP_SinapUm

## 🎯 Problema Resolvido

O repositório tinha mais de 41.000 arquivos, mas muitos eram dados de runtime (PostgreSQL, MongoDB, Redis) que não devem estar no Git.

## ✅ Solução Aplicada

1. **`.gitignore` atualizado** - Agora ignora:
   - Dados de runtime dos serviços (`pg_data/`, `mongo_data/`, `redis_data/`)
   - Arquivos Python compilados (`__pycache__/`, `*.pyc`)
   - Arquivos de log (`*.log`)
   - Arquivos estáticos gerados (`staticfiles/`)
   - Arquivos temporários e de cache

2. **Script de limpeza criado** - `limpar_arquivos_desnecessarios.sh`

## 📝 Como Fazer Commit Corretamente

### Opção 1: Commit Seletivo (Recomendado)

```bash
# 1. Ver o que será commitado
git status

# 2. Adicionar arquivos específicos
git add .gitignore
git add app_sinapum/
git add setup/
git add requirements.txt
git add *.md
git add Dockerfile docker-compose.yml

# 3. Verificar o que será commitado
git status

# 4. Fazer commit
git commit -m "Sua mensagem de commit"
```

### Opção 2: Usar Script de Limpeza Primeiro

```bash
# 1. Limpar arquivos desnecessários
./limpar_arquivos_desnecessarios.sh

# 2. Ver o que será commitado
git status

# 3. Adicionar tudo (agora seguro)
git add .

# 4. Verificar novamente
git status

# 5. Fazer commit
git commit -m "Sua mensagem de commit"
```

### Opção 3: Commit Interativo

```bash
# Adicionar arquivos interativamente
git add -i

# Ou usar modo patch (escolher partes específicas)
git add -p
```

## ⚠️ Arquivos que NÃO Devem ser Commitados

- ✅ **DEVEM estar no .gitignore:**
  - `services/**/pg_data/` (dados PostgreSQL)
  - `services/**/mongo_data/` (dados MongoDB)
  - `services/**/redis_data/` (dados Redis)
  - `__pycache__/` e `*.pyc` (arquivos Python compilados)
  - `*.log` (arquivos de log)
  - `staticfiles/` (arquivos estáticos gerados)
  - `.env` (variáveis de ambiente - use `.env.example`)

- ✅ **DEVEM ser commitados:**
  - Código fonte (`.py`)
  - Templates (`.html`)
  - Migrações Django (`migrations/*.py`)
  - Arquivos de configuração (`docker-compose.yml`, `Dockerfile`)
  - Documentação (`.md`)
  - `requirements.txt`
  - `.gitignore`

## 🔍 Verificar Antes de Commitar

```bash
# Ver quantos arquivos serão adicionados
git status --short | wc -l

# Ver apenas arquivos não rastreados
git status --porcelain | grep "^??" | wc -l

# Ver arquivos que serão commitados
git diff --cached --name-only

# Ver tamanho dos arquivos que serão commitados
git diff --cached --stat
```

## 🚨 Se Aparecerem Muitos Arquivos

Se ao fazer `git add .` aparecerem mais de 100 arquivos:

1. **PARE** e verifique:
   ```bash
   git status
   ```

2. **Verifique se o .gitignore está funcionando:**
   ```bash
   git check-ignore services/evolution_api/pg_data/
   # Deve retornar: services/evolution_api/pg_data/
   ```

3. **Se não estiver ignorando, atualize o .gitignore e limpe:**
   ```bash
   ./limpar_arquivos_desnecessarios.sh
   git status
   ```

## 📊 Status Atual

- **Arquivos rastreados:** ~70 arquivos
- **Arquivos modificados/não rastreados:** ~40 arquivos
- **Arquivos ignorados:** ~41.000+ arquivos (dados de runtime)

## 💡 Dica

Sempre use `git status` antes de `git add .` para ver o que será adicionado!

