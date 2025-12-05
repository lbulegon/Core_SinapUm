# 🧹 Como Limpar e Organizar o arquivo .env

Seu arquivo `.env` estava com muitas duplicações. Siga estes passos para organizá-lo:

## 📋 Passo a Passo

### 1. No Servidor, faça backup do .env atual

```bash
ssh root@69.169.102.84
cd /opt/openmind-ai
cp .env .env.backup
```

### 2. Copie o novo arquivo .env limpo

**Opção A - Do seu computador (PowerShell):**

```powershell
# Copiar arquivo limpo
scp .env.clean root@69.169.102.84:/opt/openmind-ai/.env
```

**Opção B - Criar manualmente no servidor:**

```bash
# No servidor
cd /opt/openmind-ai
nano .env
```

Copie e cole o conteúdo do arquivo `ENV_EXAMPLE.txt` ou use o `../.env.clean` como base.

### 3. Verificar se está correto

```bash
# No servidor
cd /opt/openmind-ai

# Verificar se não há duplicações
grep -n "OPENMIND_ORG_API_KEY" .env
# Deve aparecer apenas 1 linha

# Verificar se não há duplicações do modelo
grep -n "OPENMIND_ORG_MODEL" .env
# Deve aparecer apenas 1 linha
```

### 4. Reiniciar o serviço

```bash
systemctl restart openmind-ai
systemctl status openmind-ai
```

### 5. Verificar se está funcionando

```bash
# Ver logs
journalctl -u openmind-ai -n 20

# Testar API
curl http://localhost:8000/health
```

## ✅ Arquivos Disponíveis

- **`ENV_EXAMPLE.txt`** - Template completo com documentação
- **`.env.clean`** - Arquivo .env limpo pronto para usar

## 🔍 O que foi corrigido?

❌ **Antes (confuso):**
- Variáveis duplicadas múltiplas vezes
- Sem organização por seções
- Difícil de ler e manter

✅ **Depois (organizado):**
- Cada variável aparece apenas 1 vez
- Organizado por seções lógicas
- Comentários explicativos
- Fácil de manter e atualizar

## 📝 Estrutura do novo .env

```
1. Configurações do Servidor
2. API Keys - OpenMind.org
3. API Key - Autenticação
4. Configurações de Imagem
5. Rate Limiting
6. CORS
7. Logging
8. Grafana/Loki
```

## ⚠️ Importante

- O arquivo `.env` **nunca** deve ser commitado no Git (contém chaves secretas)
- Sempre use `ENV_EXAMPLE.txt` como template no repositório
- Mantenha backups do `.env` antes de fazer mudanças

