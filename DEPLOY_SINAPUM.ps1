# Script de Deploy Automatizado para SinapUm (PowerShell)
# Atualiza o código do OpenMind AI Server no servidor SinapUm

param(
    [string]$ServerIP = "69.169.102.84",
    [string]$ServerUser = "root",
    [string]$RemotePath = "/opt/openmind-ai",
    [string]$LocalPath = ".",
    [switch]$SkipBackup,
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

# Verificar se OpenSSH está disponível
if (-not (Get-Command ssh -ErrorAction SilentlyContinue)) {
    Write-ColorOutput Red "❌ Erro: OpenSSH não encontrado. Instale OpenSSH Client:"
    Write-Output "  Add-WindowsCapability -Online -Name OpenSSH.Client~~~~0.0.1.0"
    exit 1
}

Write-ColorOutput Cyan "🚀 Script de Deploy - OpenMind AI para SinapUm"
Write-ColorOutput Cyan "================================================"
Write-Output ""
Write-Output "Servidor: $ServerUser@$ServerIP"
Write-Output "Caminho remoto: $RemotePath"
Write-Output "Caminho local: $LocalPath"
Write-Output ""

if ($DryRun) {
    Write-ColorOutput Yellow "⚠️  MODO DRY-RUN - Nenhuma alteração será feita"
    Write-Output ""
}

# Solicitar confirmação
$confirmation = Read-Host "Continuar com o deploy? (S/N)"
if ($confirmation -ne "S" -and $confirmation -ne "s") {
    Write-ColorOutput Yellow "Deploy cancelado pelo usuário."
    exit 0
}

# Verificar se o diretório local existe
if (-not (Test-Path $LocalPath)) {
    Write-ColorOutput Red "❌ Erro: Diretório local não encontrado: $LocalPath"
    exit 1
}

# 1. Verificar conexão com servidor
Write-ColorOutput Cyan "`n[1/8] Verificando conexão com servidor..."
if (-not $DryRun) {
    $testConnection = ssh -o ConnectTimeout=5 -o BatchMode=yes "$ServerUser@$ServerIP" "echo 'OK'" 2>&1
    if ($LASTEXITCODE -ne 0) {
        Write-ColorOutput Yellow "⚠️  Teste de conexão falhou. Você precisará inserir a senha."
    } else {
        Write-ColorOutput Green "✅ Conexão estabelecida"
    }
}

# 2. Criar backup (opcional)
if (-not $SkipBackup -and -not $DryRun) {
    Write-ColorOutput Cyan "`n[2/8] Criando backup do código atual..."
    $backupDir = "$RemotePath/backup_$(Get-Date -Format 'yyyyMMdd_HHmmss')"
    ssh "$ServerUser@$ServerIP" "mkdir -p $backupDir && cp -r $RemotePath/app $backupDir/ 2>/dev/null || true"
    Write-ColorOutput Green "✅ Backup criado em: $backupDir"
} elseif ($DryRun) {
    Write-ColorOutput Cyan "`n[2/8] [DRY-RUN] Criaria backup em: $RemotePath/backup_..."
}

# 3. Verificar estrutura no servidor
Write-ColorOutput Cyan "`n[3/8] Verificando estrutura no servidor..."
if (-not $DryRun) {
    ssh "$ServerUser@$ServerIP" "
        mkdir -p $RemotePath/app
        mkdir -p /var/log/openmind-ai
        chmod 755 /var/log/openmind-ai
        echo '✅ Estrutura criada'
    "
}

# 4. Copiar arquivos Python da aplicação
Write-ColorOutput Cyan "`n[4/8] Copiando arquivos da aplicação..."
$filesToCopy = @(
    "app",
    "requirements.txt",
    "promtail-config.yml",
    "ENV_EXAMPLE.txt"
)

foreach ($file in $filesToCopy) {
    if (Test-Path "$LocalPath/$file") {
        if (-not $DryRun) {
            Write-Output "  → Copiando $file..."
            scp -r "$LocalPath/$file" "${ServerUser}@${ServerIP}:${RemotePath}/"
            if ($LASTEXITCODE -eq 0) {
                Write-ColorOutput Green "    ✅ $file copiado"
            } else {
                Write-ColorOutput Red "    ❌ Erro ao copiar $file"
            }
        } else {
            Write-Output "  → [DRY-RUN] Copiaria $file"
        }
    } else {
        Write-ColorOutput Yellow "  ⚠️  Arquivo não encontrado: $file (pulando)"
    }
}

# 5. Instalar dependências Python
Write-ColorOutput Cyan "`n[5/8] Instalando dependências Python..."
if (-not $DryRun) {
    ssh "$ServerUser@$ServerIP" "
        cd $RemotePath
        if [ -d venv ]; then
            source venv/bin/activate
        else
            python3 -m venv venv
            source venv/bin/activate
        fi
        pip install --upgrade pip
        pip install -r requirements.txt
        echo '✅ Dependências instaladas'
    "
} else {
    Write-Output "  [DRY-RUN] Instalaria dependências do requirements.txt"
}

# 6. Aplicar permissões
Write-ColorOutput Cyan "`n[6/8] Aplicando permissões..."
if (-not $DryRun) {
    ssh "$ServerUser@$ServerIP" "
        chmod -R 755 $RemotePath/app
        chmod 644 $RemotePath/promtail-config.yml 2>/dev/null || true
        chmod 644 $RemotePath/requirements.txt 2>/dev/null || true
        echo '✅ Permissões aplicadas'
    "
}

# 7. Reiniciar serviço
Write-ColorOutput Cyan "`n[7/8] Reiniciando serviço openmind-ai..."
if (-not $DryRun) {
    ssh "$ServerUser@$ServerIP" "
        if systemctl is-active --quiet openmind-ai; then
            systemctl restart openmind-ai
            sleep 2
            if systemctl is-active --quiet openmind-ai; then
                echo '✅ Serviço reiniciado com sucesso'
            else
                echo '❌ Erro: Serviço não está rodando após reinício'
                systemctl status openmind-ai --no-pager -l
                exit 1
            fi
        else
            echo '⚠️  Serviço não está rodando. Iniciando...'
            systemctl start openmind-ai
        fi
    "
} else {
    Write-Output "  [DRY-RUN] Reiniciaria o serviço openmind-ai"
}

# 8. Verificar saúde do serviço
Write-ColorOutput Cyan "`n[8/8] Verificando saúde do serviço..."
if (-not $DryRun) {
    Start-Sleep -Seconds 3
    $healthCheck = ssh "$ServerUser@$ServerIP" "
        systemctl status openmind-ai --no-pager | head -5
        curl -s http://localhost:8000/health 2>/dev/null || echo 'Health endpoint não disponível'
    "
    Write-Output $healthCheck
    
    # Verificar logs recentes
    Write-ColorOutput Cyan "`n📋 Últimas linhas dos logs:"
    ssh "$ServerUser@$ServerIP" "journalctl -u openmind-ai -n 10 --no-pager"
}

# Resumo
Write-ColorOutput Cyan "`n================================================"
Write-ColorOutput Green "✅ Deploy concluído!"
Write-Output ""
Write-Output "Próximos passos:"
Write-Output "  1. Verificar logs: ssh $ServerUser@$ServerIP 'journalctl -u openmind-ai -f'"
Write-Output "  2. Verificar logs estruturados: ssh $ServerUser@$ServerIP 'tail -f /var/log/openmind-ai/app.log'"
Write-Output "  3. Configurar Promtail com: $RemotePath/promtail-config.yml"
Write-Output ""
