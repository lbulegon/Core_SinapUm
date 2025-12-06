# 🚀 Deploy das Melhorias - Padrão JSON Évora

## 📋 O Que Foi Criado

### Arquivos Python

1. **`app/core/image_analyzer_evora.py`**
   - Analisador de imagens com prompt detalhado
   - Geração automática de SKU no padrão Évora
   - Parsing robusto de respostas JSON
   - Tratamento completo de erros

2. **`app/api/v1/endpoints/analyze_evora.py`**
   - Endpoint atualizado para padrão Évora
   - Validação de imagens
   - Logging estruturado
   - Metadados completos na resposta

### Scripts de Deploy

1. **`DEPLOY_MELHORIAS_EVORA.ps1`** - Windows PowerShell
2. **`DEPLOY_MELHORIAS_EVORA.sh`** - Linux/Mac

## ⚠️ IMPORTANTE - Antes de Fazer Deploy

### Verificar Estrutura no Servidor

O código assume que você tem:
- `app/core/` - Para utilitários
- `app/api/v1/endpoints/` - Para endpoints

### Atualizar Imports (Se Necessário)

Você pode precisar atualizar `main.py` ou o arquivo de rotas para usar o novo endpoint:

```python
# Opção 1: Substituir endpoint antigo
from app.api.v1.endpoints.analyze_evora import router as analyze_router
app.include_router(analyze_router, prefix="/api/v1", tags=["Análise"])

# Opção 2: Manter ambos (endpoint antigo e novo)
from app.api.v1.endpoints.analyze_evora import router as analyze_evora_router
app.include_router(analyze_evora_router, prefix="/api/v1", tags=["Análise Évora"])
```

## 🚀 Como Fazer Deploy

### Opção 1: Script PowerShell (Windows)

```powershell
.\DEPLOY_MELHORIAS_EVORA.ps1

# Com dry-run (testar sem fazer mudanças)
.\DEPLOY_MELHORIAS_EVORA.ps1 -DryRun
```

### Opção 2: Script Bash (Linux/Mac)

```bash
chmod +x DEPLOY_MELHORIAS_EVORA.sh
./DEPLOY_MELHORIAS_EVORA.sh

# Com parâmetros
./DEPLOY_MELHORIAS_EVORA.sh 69.169.102.84 root
```

### Opção 3: Manual

```bash
# 1. Backup
ssh root@69.169.102.84 "cd /opt/openmind-ai && cp -r app app.backup"

# 2. Copiar arquivos
scp app/core/image_analyzer_evora.py root@69.169.102.84:/opt/openmind-ai/app/core/
scp app/api/v1/endpoints/analyze_evora.py root@69.169.102.84:/opt/openmind-ai/app/api/v1/endpoints/

# 3. Atualizar imports (se necessário)
ssh root@69.169.102.84 "cd /opt/openmind-ai/app && nano main.py"

# 4. Reiniciar
ssh root@69.169.102.84 "systemctl restart openmind-ai"
```

## ✅ Após o Deploy

### Testar Análise

```powershell
.\OBTER_ANALISE_JSON_SIMPLES.ps1 -Imagem "img\coca.jpg" -ApiKey "sua_api_key" -SalvarArquivo
```

### Verificar Resultado

O JSON retornado deve agora conter:
- ✅ Nome completo do produto (não genérico)
- ✅ Categoria específica
- ✅ Descrição comercial detalhada
- ✅ Características extraídas
- ✅ SKU no padrão Évora (EVR-XXX-XXX-XXX)
- ✅ Código de barras (se visível)
- ✅ Compatibilidade
- ✅ Dimensões (se estimável)

### Verificar Logs

```bash
ssh root@69.169.102.84 "journalctl -u openmind-ai -f"
```

## 🔧 Troubleshooting

### Erro: Módulo não encontrado

```bash
# Verificar se arquivo foi copiado
ssh root@69.169.102.84 "ls -la /opt/openmind-ai/app/core/image_analyzer_evora.py"

# Verificar imports
ssh root@69.169.102.84 "cd /opt/openmind-ai/app && python3 -c 'from app.core.image_analyzer_evora import analyze_image_evora'"
```

### Erro: Endpoint não encontrado

```bash
# Verificar rotas no main.py
ssh root@69.169.102.84 "cd /opt/openmind-ai/app && grep -r 'analyze' main.py"
```

### Rollback

```bash
# Restaurar backup
ssh root@69.169.102.84 "cd /opt/openmind-ai && rm -rf app && cp -r app.backup app && systemctl restart openmind-ai"
```

## 📝 Notas

- O código mantém compatibilidade com a estrutura atual
- Logs detalhados para debug
- Tratamento robusto de erros
- Geração automática de SKU

---

**Pronto para fazer deploy!** 🚀


