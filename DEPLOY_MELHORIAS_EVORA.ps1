# Script de Deploy PowerShell para Melhorias do Padrão Évora

param(
    [string]$ServerIP = "69.169.102.84",
    [string]$ServerUser = "root",
    [string]$RemotePath = "/opt/openmind-ai",
    [switch]$DryRun
)

$APP_PATH = "$RemotePath/app"

function Write-Step($Message) {
    Write-Host "[INFO] $Message" -ForegroundColor Cyan
}

function Write-Success($Message) {
    Write-Host "[OK] $Message" -ForegroundColor Green
}

function Write-Error($Message) {
    Write-Host "[ERRO] $Message" -ForegroundColor Red
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Deploy Melhorias Padrão Évora" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

if ($DryRun) {
    Write-Host "[AVISO] MODO DRY-RUN - Nenhuma alteracao sera feita" -ForegroundColor Yellow
    Write-Host ""
}

# Verificar arquivos locais
if (-not (Test-Path "app\core\image_analyzer_evora.py")) {
    Write-Error "Arquivo app\core\image_analyzer_evora.py nao encontrado!"
    exit 1
}

if (-not (Test-Path "app\api\v1\endpoints\analyze_evora.py")) {
    Write-Error "Arquivo app\api\v1\endpoints\analyze_evora.py nao encontrado!"
    exit 1
}

# Confirmar
$confirmation = Read-Host "Continuar com o deploy? (S/N)"
if ($confirmation -ne "S" -and $confirmation -ne "s") {
    Write-Host "Deploy cancelado." -ForegroundColor Yellow
    exit 0
}

# 1. Backup
Write-Step "Fazendo backup do codigo atual..."
if (-not $DryRun) {
    $backupResult = ssh "$ServerUser@$ServerIP" "
        cd $RemotePath
        BACKUP_DIR=\"backups/backup_evora_\$(date +%Y%m%d_%H%M%S)\"
        mkdir -p \"\$BACKUP_DIR\"
        cp -r app \"\$BACKUP_DIR/\"
        echo \"BACKUP_OK:\$BACKUP_DIR\"
    " 2>&1
    
    if ($backupResult -match 'BACKUP_OK:') {
        $backupPath = ($backupResult -split 'BACKUP_OK:')[1].Trim()
        Write-Success "Backup criado em: $backupPath"
    } else {
        Write-Error "Erro ao criar backup: $backupResult"
        exit 1
    }
}

# 2. Criar diretórios se necessário
Write-Step "Criando diretorios se necessario..."
if (-not $DryRun) {
    ssh "$ServerUser@$ServerIP" "
        mkdir -p $APP_PATH/core
        mkdir -p $APP_PATH/api/v1/endpoints
    " | Out-Null
}

# 3. Copiar arquivos
Write-Step "Copiando novos arquivos..."
if (-not $DryRun) {
    scp "app\core\image_analyzer_evora.py" "${ServerUser}@${ServerIP}:${APP_PATH}/core/" 2>&1 | Out-Null
    if ($LASTEXITCODE -eq 0) {
        Write-Success "image_analyzer_evora.py copiado"
    } else {
        Write-Error "Erro ao copiar image_analyzer_evora.py"
        exit 1
    }
    
    scp "app\api\v1\endpoints\analyze_evora.py" "${ServerUser}@${ServerIP}:${APP_PATH}/api/v1/endpoints/" 2>&1 | Out-Null
    if ($LASTEXITCODE -eq 0) {
        Write-Success "analyze_evora.py copiado"
    } else {
        Write-Error "Erro ao copiar analyze_evora.py"
        exit 1
    }
} else {
    Write-Host "  [DRY-RUN] Copiaria arquivos para o servidor"
}

# 4. Verificar se precisa atualizar imports
Write-Step "Verificando se precisa atualizar imports..."
if (-not $DryRun) {
    $needsUpdate = ssh "$ServerUser@$ServerIP" "
        cd $APP_PATH
        if grep -q 'from app.api.v1.endpoints import analyze' main.py 2>/dev/null; then
            echo 'NEEDS_UPDATE'
        else
            echo 'OK'
        fi
    " 2>&1
    
    if ($needsUpdate -match 'NEEDS_UPDATE') {
        Write-Host "  [AVISO] Pode ser necessario atualizar main.py para usar analyze_evora" -ForegroundColor Yellow
        Write-Host "  Verifique o arquivo main.py no servidor" -ForegroundColor Yellow
    }
}

# 5. Reiniciar serviço
Write-Step "Reiniciando servico..."
if (-not $DryRun) {
    $restartResult = ssh "$ServerUser@$ServerIP" "
        systemctl restart openmind-ai
        sleep 3
        if systemctl is-active --quiet openmind-ai; then
            echo 'SERVICE_OK'
        else
            echo 'SERVICE_FAILED'
            systemctl status openmind-ai --no-pager -l | head -20
        fi
    " 2>&1
    
    if ($restartResult -match 'SERVICE_OK') {
        Write-Success "Servico reiniciado com sucesso"
    } else {
        Write-Error "Erro ao reiniciar servico"
        Write-Host $restartResult
        exit 1
    }
} else {
    Write-Host "  [DRY-RUN] Reiniciaria o servico openmind-ai"
}

# 6. Verificar saúde
Write-Step "Verificando saude do servico..."
if (-not $DryRun) {
    Start-Sleep -Seconds 2
    
    $healthCheck = ssh "$ServerUser@$ServerIP" "
        systemctl status openmind-ai --no-pager | head -5
        echo '---'
        curl -s http://localhost:8000/health 2>/dev/null || echo 'Health endpoint nao disponivel'
    " 2>&1
    
    Write-Host $healthCheck
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Success "Deploy concluido!"
Write-Host ""
Write-Host "Proximos passos:" -ForegroundColor Cyan
Write-Host "  1. Testar analise:" -ForegroundColor White
Write-Host "     .\OBTER_ANALISE_JSON_SIMPLES.ps1 -Imagem 'img\coca.jpg' -ApiKey 'sua_key'" -ForegroundColor Gray
Write-Host ""
Write-Host "  2. Verificar logs:" -ForegroundColor White
Write-Host "     ssh $ServerUser@$ServerIP 'journalctl -u openmind-ai -f'" -ForegroundColor Gray
Write-Host ""
Write-Host "  3. Validar JSON retornado:" -ForegroundColor White
Write-Host "     Verificar se agora retorna dados detalhados no padrao Evora" -ForegroundColor Gray
Write-Host ""

