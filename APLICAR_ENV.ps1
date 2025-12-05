# Script para Aplicar arquivo .env Limpo no Servidor SinapUm
# Remove duplicações e organiza as variáveis de ambiente

param(
    [string]$ServerIP = "69.169.102.84",
    [string]$ServerUser = "root",
    [string]$RemotePath = "/opt/openmind-ai",
    [switch]$DryRun
)

# Cores para output
function Write-ColorOutput($ForegroundColor) {
    $fc = $host.UI.RawUI.ForegroundColor
    $host.UI.RawUI.ForegroundColor = $ForegroundColor
    if ($args) {
        Write-Output $args
    }
    $host.UI.RawUI.ForegroundColor = $fc
}

Write-ColorOutput Cyan "Aplicar arquivo .env Limpo no Servidor SinapUm"
Write-ColorOutput Cyan "=================================================="
Write-Output ""
Write-Output "Servidor: $ServerUser@$ServerIP"
Write-Output "Caminho: $RemotePath"
Write-Output ""

if ($DryRun) {
    Write-ColorOutput Yellow "[AVISO] MODO DRY-RUN - Nenhuma alteracao sera feita"
    Write-Output ""
}

# Verificar se OpenSSH está disponível
if (-not (Get-Command ssh -ErrorAction SilentlyContinue)) {
    Write-ColorOutput Red "❌ Erro: OpenSSH não encontrado."
    Write-Output "  Instale: Add-WindowsCapability -Online -Name OpenSSH.Client~~~~0.0.1.0"
    exit 1
}

# Verificar se ENV_EXAMPLE.txt existe
if (-not (Test-Path "ENV_EXAMPLE.txt")) {
    Write-ColorOutput Red "❌ Erro: Arquivo ENV_EXAMPLE.txt não encontrado!"
    Write-Output "  Certifique-se de estar no diretório correto."
    exit 1
}

# Confirmar ação
$confirmation = Read-Host "Continuar com a aplicação do .env limpo? (S/N)"
if ($confirmation -ne "S" -and $confirmation -ne "s") {
    Write-ColorOutput Yellow "Operação cancelada pelo usuário."
    exit 0
}

Write-ColorOutput Cyan "`n[1/6] Criando arquivo .env limpo a partir do ENV_EXAMPLE.txt..."

# Ler ENV_EXAMPLE.txt e filtrar apenas variáveis de ambiente
# Manter apenas linhas que começam com letra maiúscula seguida de letras/underscores e =
$envVars = Get-Content "ENV_EXAMPLE.txt" | Where-Object {
    $_ -match '^[A-Z_][A-Z0-9_]*=.*' -and $_ -notmatch '^#'
} | ForEach-Object {
    # Remover espaços no início e fim
    $_.Trim()
}

# Remover duplicações mantendo a primeira ocorrência
$uniqueVars = @{}
$envVars | ForEach-Object {
    if ($_ -match '^([A-Z_][A-Z0-9_]*)=') {
        $varName = $matches[1]
        if (-not $uniqueVars.ContainsKey($varName)) {
            $uniqueVars[$varName] = $_
        }
    }
}

# Criar arquivo .env temporário com quebras de linha
$tempEnvFile = ".env.temp"
$uniqueVars.Values | Out-File -FilePath $tempEnvFile -Encoding utf8

Write-ColorOutput Green "✅ Arquivo .env temporário criado"

# Verificar duplicações localmente
Write-ColorOutput Cyan "`n[2/6] Verificando duplicações no arquivo..."
$duplicates = $envVars | ForEach-Object {
    if ($_ -match '^([A-Z_]+)=') {
        $matches[1]
    }
} | Group-Object | Where-Object { $_.Count -gt 1 }

if ($duplicates) {
    Write-ColorOutput Yellow "⚠️  Encontradas duplicações:"
    $duplicates | ForEach-Object {
        Write-Output "  - $($_.Name) aparece $($_.Count) vezes"
    }
    Write-ColorOutput Yellow "  Continuando mesmo assim..."
} else {
    Write-ColorOutput Green "✅ Nenhuma duplicação encontrada"
}

# Fazer backup do .env atual no servidor
Write-ColorOutput Cyan "`n[3/6] Fazendo backup do .env atual no servidor..."
if (-not $DryRun) {
    $backupResult = ssh "$ServerUser@$ServerIP" "
        cd $RemotePath
        if [ -f .env ]; then
            cp .env .env.backup_$(date +%Y%m%d_%H%M%S)
            echo 'BACKUP_OK'
        else
            echo 'NO_ENV_FILE'
        fi
    " 2>&1
    
    if ($backupResult -match 'BACKUP_OK') {
        Write-ColorOutput Green "✅ Backup criado com sucesso"
    } elseif ($backupResult -match 'NO_ENV_FILE') {
        Write-ColorOutput Yellow "⚠️  Arquivo .env não encontrado no servidor (será criado novo)"
    } else {
        Write-ColorOutput Yellow "⚠️  Aviso ao fazer backup: $backupResult"
    }
} else {
    Write-Output "  [DRY-RUN] Faria backup do .env atual"
}

# Copiar arquivo .env limpo para o servidor
Write-ColorOutput Cyan "`n[4/6] Copiando arquivo .env limpo para o servidor..."
if (-not $DryRun) {
    scp $tempEnvFile "${ServerUser}@${ServerIP}:${RemotePath}/.env" 2>&1 | Out-Null
    if ($LASTEXITCODE -eq 0) {
        Write-ColorOutput Green "✅ Arquivo .env copiado com sucesso"
    } else {
        Write-ColorOutput Red "❌ Erro ao copiar arquivo .env"
        Remove-Item $tempEnvFile -ErrorAction SilentlyContinue
        exit 1
    }
} else {
    Write-Output "  [DRY-RUN] Copiaria arquivo .env para o servidor"
}

# Limpar arquivo temporário
Remove-Item $tempEnvFile -ErrorAction SilentlyContinue

# Verificar duplicações no servidor
Write-ColorOutput Cyan "`n[5/6] Verificando duplicações no servidor..."
if (-not $DryRun) {
    $serverCheck = ssh "$ServerUser@$ServerIP" "
        cd $RemotePath
        if [ -f .env ]; then
            echo 'FILE_EXISTS'
            # Verificar duplicações
            grep -c '^OPENMIND_ORG_API_KEY=' .env
            grep -c '^OPENMIND_ORG_MODEL=' .env
        else
            echo 'FILE_NOT_FOUND'
        fi
    " 2>&1
    
    if ($serverCheck -match 'FILE_EXISTS') {
        $lines = $serverCheck -split "`n"
        $keyCount = ($lines | Where-Object { $_ -match '^\d+$' } | Select-Object -First 1)
        $modelCount = ($lines | Where-Object { $_ -match '^\d+$' } | Select-Object -Skip 1 -First 1)
        
        if ($keyCount -eq "1" -and $modelCount -eq "1") {
            Write-ColorOutput Green "✅ Arquivo .env verificado - sem duplicações"
        } else {
            Write-ColorOutput Yellow "⚠️  Possíveis duplicações encontradas:"
            Write-Output "  OPENMIND_ORG_API_KEY aparece: $keyCount vezes"
            Write-Output "  OPENMIND_ORG_MODEL aparece: $modelCount vezes"
        }
    } else {
        Write-ColorOutput Red "❌ Arquivo .env não encontrado no servidor após cópia"
        exit 1
    }
} else {
    Write-Output "  [DRY-RUN] Verificaria duplicações no servidor"
}

# Reiniciar serviço
Write-ColorOutput Cyan "`n[6/6] Reiniciando serviço openmind-ai..."
if (-not $DryRun) {
    $restartResult = ssh "$ServerUser@$ServerIP" "
        systemctl restart openmind-ai
        sleep 3
        if systemctl is-active --quiet openmind-ai; then
            echo 'SERVICE_RUNNING'
        else
            echo 'SERVICE_FAILED'
            systemctl status openmind-ai --no-pager -l | head -20
        fi
    " 2>&1
    
    if ($restartResult -match 'SERVICE_RUNNING') {
        Write-ColorOutput Green "✅ Serviço reiniciado com sucesso"
    } else {
        Write-ColorOutput Red "❌ Erro ao reiniciar serviço"
        Write-Output $restartResult
        exit 1
    }
} else {
    Write-Output "  [DRY-RUN] Reiniciaria o serviço openmind-ai"
}

# Verificar saúde
Write-ColorOutput Cyan "`n[INFO] Verificando saude do servico..."
if (-not $DryRun) {
    Start-Sleep -Seconds 2
    
    # Verificar status do serviço
    $serviceStatus = ssh "$ServerUser@$ServerIP" "systemctl status openmind-ai --no-pager | head -5" 2>&1
    Write-Output $serviceStatus
    
    # Verificar erros recentes
    $errors = ssh "$ServerUser@$ServerIP" "journalctl -u openmind-ai -n 5 --no-pager | grep -i error || echo 'Sem erros recentes'" 2>&1
    Write-Output $errors
    
    # Testar endpoint de saúde
    Write-ColorOutput Cyan "`n[INFO] Testando endpoint de saude..."
    $healthEndpoint = ssh "$ServerUser@$ServerIP" "curl -s http://localhost:8000/health 2>/dev/null || echo 'Endpoint nao disponivel'" 2>&1
    if ($healthEndpoint -match 'ok|healthy|200') {
        Write-ColorOutput Green "✅ Endpoint de saude respondendo"
    } else {
        Write-ColorOutput Yellow "⚠️  Endpoint de saude nao esta respondendo: $healthEndpoint"
    }
}

# Resumo
Write-ColorOutput Cyan "`n=================================================="
Write-ColorOutput Green "✅ Arquivo .env limpo aplicado com sucesso!"
Write-Output ""
Write-Output "Próximos passos:"
Write-Output "  1. Verificar logs: ssh $ServerUser@$ServerIP 'journalctl -u openmind-ai -f'"
Write-Output "  2. Ver logs estruturados: ssh $ServerUser@$ServerIP 'tail -f /var/log/openmind-ai/app.log'"
Write-Output "  3. Verificar .env no servidor: ssh $ServerUser@$ServerIP 'cat $RemotePath/.env'"
Write-Output ""
Write-Output "Backup salvo em: $RemotePath/.env.backup_*"
Write-Output ""

