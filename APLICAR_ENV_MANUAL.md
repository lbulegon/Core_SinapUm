# 🔧 Aplicar .env Limpo - Modo Manual

Se preferir fazer manualmente ao invés do script automatizado:

## Opção 1: Via SCP (Recomendado)

### 1. Criar arquivo .env local limpo

```powershell
# No PowerShell, no diretório do projeto
cd C:\Users\lbule\OneDrive\Documentos\Source\SinapUm

# Criar arquivo .env sem comentários a partir do ENV_EXAMPLE.txt
Get-Content ENV_EXAMPLE.txt | Where-Object { $_ -match '^[A-Z_]+=.*' } | Out-File -FilePath .env -Encoding utf8
```

### 2. Fazer backup no servidor

```powershell
ssh root@69.169.102.84 "cd /opt/openmind-ai && cp .env .env.backup_$(Get-Date -Format 'yyyyMMdd_HHmmss')"
```

### 3. Copiar arquivo .env para servidor

```powershell
scp .env root@69.169.102.84:/opt/openmind-ai/.env
```

### 4. Verificar e reiniciar

```powershell
# Verificar duplicações
ssh root@69.169.102.84 "cd /opt/openmind-ai && grep -c '^OPENMIND_ORG_API_KEY=' .env"
# Deve retornar: 1

# Reiniciar serviço
ssh root@69.169.102.84 "systemctl restart openmind-ai && systemctl status openmind-ai"
```

## Opção 2: Editar diretamente no servidor

### 1. Conectar ao servidor

```powershell
ssh root@69.169.102.84
```

### 2. Fazer backup

```bash
cd /opt/openmind-ai
cp .env .env.backup_$(date +%Y%m%d_%H%M%S)
```

### 3. Editar arquivo

```bash
nano .env
```

**Cole este conteúdo limpo:**

```env
HOST=0.0.0.0
PORT=8000
OPENMIND_ORG_API_KEY=om1_live_7d4102a1bf72cc497d7651beb6a98292764b1f77df947c82d086506038ea6b9921efb9d9833045d1
OPENMIND_ORG_BASE_URL=https://api.openmind.org/api/core/openai
OPENMIND_ORG_MODEL=qwen2.5-vl-72b-instruct
OPENMIND_AI_API_KEY=om1_live_7d4102a1bf72cc497d7651beb6a98292764b1f77df947c82d086506038ea6b9921efb9d9833045d1
MAX_IMAGE_SIZE_MB=10
ALLOWED_IMAGE_FORMATS=jpeg,jpg,png,webp
IMAGE_MAX_DIMENSION=2048
RATE_LIMIT_PER_MINUTE=100
CORS_ORIGINS=*
LOG_LEVEL=INFO
LOG_FORMAT=json
LOG_DIR=/var/log/openmind-ai
LOKI_ENABLED=True
LOKI_URL=http://localhost:3100/loki/api/v1/push
```

Salve com `Ctrl+O`, Enter, `Ctrl+X`

### 4. Verificar e reiniciar

```bash
# Verificar duplicações
grep -c '^OPENMIND_ORG_API_KEY=' .env
grep -c '^OPENMIND_ORG_MODEL=' .env
# Ambos devem retornar: 1

# Reiniciar serviço
systemctl restart openmind-ai
systemctl status openmind-ai

# Ver logs
journalctl -u openmind-ai -n 20
```

## Verificação Final

```bash
# Verificar se não há duplicações
cd /opt/openmind-ai
for var in OPENMIND_ORG_API_KEY OPENMIND_ORG_MODEL OPENMIND_ORG_BASE_URL; do
    count=$(grep -c "^${var}=" .env)
    echo "$var aparece $count vezes"
done

# Testar API
curl http://localhost:8000/health
```

## Restaurar Backup (se necessário)

```bash
cd /opt/openmind-ai
cp .env.backup_* .env
systemctl restart openmind-ai
```

