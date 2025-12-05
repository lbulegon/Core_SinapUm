# 🔧 Configurar Git para GitHub

Guia para configurar o Git e resolver erros ao fazer commit.

## ⚠️ Erro Comum

```
Make sure you configure your "user.name" and "user.email" in git.
```

Este erro ocorre quando o Git não está configurado com suas credenciais.

## ✅ Solução: Configurar Git

### 1. Configurar Nome do Usuário

```bash
git config --global user.name "Seu Nome"
```

**Exemplo:**
```bash
git config --global user.name "Liandro Bulegon"
```

### 2. Configurar Email

```bash
git config --global user.email "seu-email@exemplo.com"
```

**Exemplo:**
```bash
git config --global user.email "lbulegon@exemplo.com"
```

### 3. Verificar Configuração

```bash
git config --global user.name
git config --global user.email
```

## 🚀 Fazer Commit Após Configurar

Depois de configurar, você pode fazer commit normalmente:

```bash
cd /root/SinapUm
git add .
git commit -m "Mensagem do commit"
git push origin main
```

## 📋 Configurações Recomendadas

### Configuração Global (para todos os projetos)

```bash
git config --global user.name "Seu Nome"
git config --global user.email "seu-email@exemplo.com"
```

### Configuração Local (apenas este projeto)

```bash
cd /root/SinapUm
git config user.name "Seu Nome"
git config user.email "seu-email@exemplo.com"
```

### Outras Configurações Úteis

```bash
# Editor padrão
git config --global core.editor "nano"

# Linha final de arquivo
git config --global core.autocrlf input

# Ver todas as configurações
git config --list
```

## 🔐 Autenticação no GitHub

Se precisar fazer push, você pode precisar configurar autenticação:

### Opção 1: Personal Access Token (Recomendado)

1. Criar token no GitHub: Settings → Developer settings → Personal access tokens
2. Usar token como senha ao fazer push

### Opção 2: SSH Keys

```bash
# Gerar chave SSH
ssh-keygen -t ed25519 -C "seu-email@exemplo.com"

# Adicionar chave ao ssh-agent
eval "$(ssh-agent -s)"
ssh-add ~/.ssh/id_ed25519

# Copiar chave pública
cat ~/.ssh/id_ed25519.pub
# Adicionar essa chave no GitHub: Settings → SSH and GPG keys
```

## 📝 Checklist para Primeiro Commit

- [ ] Configurar `user.name`
- [ ] Configurar `user.email`
- [ ] Verificar configurações
- [ ] Adicionar arquivos: `git add .`
- [ ] Fazer commit: `git commit -m "mensagem"`
- [ ] Fazer push: `git push origin main`

