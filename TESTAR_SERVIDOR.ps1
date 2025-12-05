# Script de Testes Automatizado para Servidor OpenMind AI
# Testa todos os endpoints e funcionalidades do servidor

param(
    [string]$ServerIP = "69.169.102.84",
    [string]$ServerUser = "root",
    [int]$Port = 8000,
    [string]$TestImage = $null
)

$BaseURL = "http://${ServerIP}:${Port}"

# Cores para output
function Write-TestResult($TestName, $Success, $Message = "") {
    if ($Success) {
        Write-Host "[OK] " -ForegroundColor Green -NoNewline
        Write-Host "$TestName" -ForegroundColor White
        if ($Message) {
            Write-Host "      $Message" -ForegroundColor Gray
        }
    } else {
        Write-Host "[ERRO] " -ForegroundColor Red -NoNewline
        Write-Host "$TestName" -ForegroundColor White
        if ($Message) {
            Write-Host "      $Message" -ForegroundColor Red
        }
    }
}

function Write-Section($Title) {
    Write-Host ""
    Write-Host "========================================" -ForegroundColor Cyan
    Write-Host $Title -ForegroundColor Cyan
    Write-Host "========================================" -ForegroundColor Cyan
    Write-Host ""
}

# Verificar se curl está disponível
if (-not (Get-Command curl -ErrorAction SilentlyContinue)) {
    Write-Host "[ERRO] curl nao encontrado. Instale ou use Invoke-WebRequest." -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Testes do Servidor OpenMind AI" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Servidor: $BaseURL" -ForegroundColor Gray
Write-Host ""

# ============================================================================
# Teste 1: Conectividade Básica
# ============================================================================
Write-Section "1. Testes de Conectividade"

# Teste 1.1: Ping básico
Write-Host "[TESTE] Verificando conectividade com servidor..." -ForegroundColor Yellow
try {
    $pingResult = Test-Connection -ComputerName $ServerIP -Count 1 -Quiet -ErrorAction SilentlyContinue
    Write-TestResult "Ping ao servidor" $pingResult
} catch {
    Write-TestResult "Ping ao servidor" $false $_.Exception.Message
}

# ============================================================================
# Teste 2: Status do Serviço (via SSH) - Opcional
# ============================================================================
Write-Section "2. Status do Servico (systemd) - Opcional"

if (Get-Command ssh -ErrorAction SilentlyContinue) {
    Write-Host "[TESTE] Verificando status do servico no servidor (opcional)..." -ForegroundColor Yellow
    Write-Host "[INFO] Este teste requer autenticacao SSH. Pulando se nao disponivel." -ForegroundColor Gray
    
    # Tentar verificar via SSH sem interação (apenas se chave SSH estiver configurada)
    try {
        $serviceStatus = ssh -o ConnectTimeout=5 -o BatchMode=yes "$ServerUser@$ServerIP" "systemctl is-active openmind-ai" 2>&1
        if ($LASTEXITCODE -eq 0 -and $serviceStatus -match "active") {
            Write-TestResult "Servico openmind-ai esta rodando" $true
        } elseif ($LASTEXITCODE -ne 0) {
            Write-Host "[INFO] SSH requer autenticacao. Testando servico via HTTP..." -ForegroundColor Yellow
            # Se não conseguir via SSH, verifica se HTTP responde (indica que serviço está rodando)
            try {
                $testResponse = Invoke-WebRequest -Uri "$BaseURL/health" -Method GET -TimeoutSec 5 -ErrorAction Stop
                Write-TestResult "Servico responde via HTTP" $true "Indica que o servico esta rodando"
            } catch {
                Write-TestResult "Servico respondendo" $false "Nao foi possivel verificar"
            }
        } else {
            Write-TestResult "Servico openmind-ai esta rodando" $false "Status: $serviceStatus"
        }
    } catch {
        Write-Host "[INFO] SSH nao configurado. Verificando servico via HTTP..." -ForegroundColor Yellow
        try {
            $testResponse = Invoke-WebRequest -Uri "$BaseURL/health" -Method GET -TimeoutSec 5 -ErrorAction Stop
            Write-TestResult "Servico responde via HTTP" $true "Indica que o servico esta rodando"
        } catch {
            Write-TestResult "Servico respondendo" $false "Nao foi possivel verificar"
        }
    }
} else {
    Write-Host "[AVISO] SSH nao disponivel. Verificando servico via HTTP..." -ForegroundColor Yellow
    try {
        $testResponse = Invoke-WebRequest -Uri "$BaseURL/health" -Method GET -TimeoutSec 5 -ErrorAction Stop
        Write-TestResult "Servico responde via HTTP" $true "Indica que o servico esta rodando"
    } catch {
        Write-TestResult "Servico respondendo" $false "Nao foi possivel verificar"
    }
}

# ============================================================================
# Teste 3: Endpoints HTTP
# ============================================================================
Write-Section "3. Testes de Endpoints HTTP"

# Teste 3.1: Health Check
Write-Host "[TESTE] Testando endpoint /health..." -ForegroundColor Yellow
try {
    $response = Invoke-WebRequest -Uri "$BaseURL/health" -Method GET -TimeoutSec 10 -ErrorAction Stop
    if ($response.StatusCode -eq 200) {
        Write-TestResult "Health Check (/health)" $true "Status: $($response.StatusCode)"
        try {
            $json = $response.Content | ConvertFrom-Json
            Write-Host "      Resposta: $($response.Content)" -ForegroundColor Gray
        } catch {
            Write-Host "      Resposta: $($response.Content)" -ForegroundColor Gray
        }
    } else {
        Write-TestResult "Health Check (/health)" $false "Status: $($response.StatusCode)"
    }
} catch {
    Write-TestResult "Health Check (/health)" $false $_.Exception.Message
}

# Teste 3.2: Root Endpoint
Write-Host "[TESTE] Testando endpoint raiz (/)..." -ForegroundColor Yellow
try {
    $response = Invoke-WebRequest -Uri "$BaseURL/" -Method GET -TimeoutSec 10 -ErrorAction Stop
    Write-TestResult "Root Endpoint (/)" $true "Status: $($response.StatusCode)"
} catch {
    Write-TestResult "Root Endpoint (/)" $false $_.Exception.Message
}

# Teste 3.3: Documentação OpenAPI
Write-Host "[TESTE] Testando endpoint de documentacao (/docs)..." -ForegroundColor Yellow
try {
    $response = Invoke-WebRequest -Uri "$BaseURL/docs" -Method GET -TimeoutSec 10 -ErrorAction Stop
    Write-TestResult "Documentacao (/docs)" $true "Status: $($response.StatusCode)"
    Write-Host "      Acesse em: $BaseURL/docs" -ForegroundColor Gray
} catch {
    Write-TestResult "Documentacao (/docs)" $false $_.Exception.Message
}

# Teste 3.4: OpenAPI JSON
Write-Host "[TESTE] Testando endpoint OpenAPI JSON (/openapi.json)..." -ForegroundColor Yellow
try {
    $response = Invoke-WebRequest -Uri "$BaseURL/openapi.json" -Method GET -TimeoutSec 10 -ErrorAction Stop
    if ($response.StatusCode -eq 200) {
        $json = $response.Content | ConvertFrom-Json
        $endpoints = $json.paths.PSObject.Properties.Name
        Write-TestResult "OpenAPI JSON (/openapi.json)" $true "Endpoints encontrados: $($endpoints.Count)"
        Write-Host "      Endpoints: $($endpoints -join ', ')" -ForegroundColor Gray
    }
} catch {
    Write-TestResult "OpenAPI JSON (/openapi.json)" $false $_.Exception.Message
}

# ============================================================================
# Teste 4: Análise de Imagem
# ============================================================================
Write-Section "4. Testes de Analise de Imagem"

# Verificar se imagem de teste foi fornecida
if (-not $TestImage) {
    Write-Host "[AVISO] Nenhuma imagem fornecida. Criando imagem de teste..." -ForegroundColor Yellow
    
    # Criar imagem de teste simples (1x1 pixel PNG)
    $testImagePath = "test_image.png"
    try {
        # Tentar criar uma imagem de teste usando .NET
        Add-Type -AssemblyName System.Drawing
        $bitmap = New-Object System.Drawing.Bitmap(100, 100)
        $graphics = [System.Drawing.Graphics]::FromImage($bitmap)
        $graphics.FillRectangle([System.Drawing.Brushes]::White, 0, 0, 100, 100)
        $graphics.DrawString("TEST", (New-Object System.Drawing.Font("Arial", 12)), [System.Drawing.Brushes]::Black, 10, 10)
        $bitmap.Save($testImagePath, [System.Drawing.Imaging.ImageFormat]::Png)
        $graphics.Dispose()
        $bitmap.Dispose()
        $TestImage = $testImagePath
        Write-Host "      Imagem de teste criada: $testImagePath" -ForegroundColor Gray
    } catch {
        Write-Host "[AVISO] Nao foi possivel criar imagem de teste automaticamente." -ForegroundColor Yellow
        Write-Host "      Use o parametro -TestImage para especificar uma imagem:" -ForegroundColor Yellow
        Write-Host "      .\TESTAR_SERVIDOR.ps1 -TestImage 'caminho/para/imagem.jpg'" -ForegroundColor Yellow
        Write-Host "[AVISO] Pulando testes de analise de imagem..." -ForegroundColor Yellow
    }
}

if ($TestImage -and (Test-Path $TestImage)) {
    Write-Host "[TESTE] Testando endpoint de analise de imagem..." -ForegroundColor Yellow
    
    try {
        # Usar a forma nativa do PowerShell para multipart/form-data
        $fileName = Split-Path $TestImage -Leaf
        $fileContentType = if ($TestImage -match '\.jpg|\.jpeg') { 'image/jpeg' } elseif ($TestImage -match '\.png') { 'image/png' } else { 'image/png' }
        
        # Criar objeto de formulário
        $form = @{
            image = Get-Item -Path $TestImage
        }
        
        $response = Invoke-RestMethod -Uri "$BaseURL/api/v1/analyze-product-image" -Method POST -Form $form -TimeoutSec 30 -ErrorAction Stop
        
        Write-TestResult "Analise de Imagem (/api/v1/analyze-product-image)" $true "Status: 200"
        
        # A resposta já vem como objeto JSON do Invoke-RestMethod
        if ($response) {
            if ($response.success) {
                Write-Host "      Analise bem-sucedida!" -ForegroundColor Gray
            }
            if ($response.request_id) {
                Write-Host "      Request ID: $($response.request_id)" -ForegroundColor Gray
            }
            if ($response.processing_time_ms) {
                Write-Host "      Tempo de processamento: $($response.processing_time_ms)ms" -ForegroundColor Gray
            }
            if ($response.analysis) {
                Write-Host "      Analise recebida com sucesso!" -ForegroundColor Gray
            }
            
            # Mostrar resposta completa (limitada)
            $jsonResponse = $response | ConvertTo-Json -Depth 5 -Compress
            Write-Host "      Resposta: $($jsonResponse.Substring(0, [Math]::Min(200, $jsonResponse.Length)))..." -ForegroundColor Gray
        }
    } catch {
        Write-TestResult "Analise de Imagem (/api/v1/analyze-product-image)" $false $_.Exception.Message
    }
    
    # Limpar imagem de teste se foi criada automaticamente
    if ($TestImage -eq "test_image.png" -and (Test-Path "test_image.png")) {
        Remove-Item "test_image.png" -ErrorAction SilentlyContinue
    }
} else {
    Write-Host "[AVISO] Imagem de teste nao encontrada. Pulando teste de analise." -ForegroundColor Yellow
}

# ============================================================================
# Teste 5: Performance
# ============================================================================
Write-Section "5. Testes de Performance"

Write-Host "[TESTE] Medindo tempo de resposta do health check..." -ForegroundColor Yellow
$times = @()
for ($i = 1; $i -le 5; $i++) {
    try {
        $stopwatch = [System.Diagnostics.Stopwatch]::StartNew()
        $response = Invoke-WebRequest -Uri "$BaseURL/health" -Method GET -TimeoutSec 5 -ErrorAction Stop
        $stopwatch.Stop()
        $times += $stopwatch.ElapsedMilliseconds
    } catch {
        # Ignorar erros neste teste
    }
}

if ($times.Count -gt 0) {
    $avgTime = ($times | Measure-Object -Average).Average
    $minTime = ($times | Measure-Object -Minimum).Minimum
    $maxTime = ($times | Measure-Object -Maximum).Maximum
    Write-TestResult "Tempo medio de resposta" $true "${avgTime}ms (min: ${minTime}ms, max: ${maxTime}ms)"
} else {
    Write-TestResult "Tempo medio de resposta" $false "Nao foi possivel medir"
}

# ============================================================================
# Resumo Final
# ============================================================================
Write-Section "Resumo dos Testes"

Write-Host "Testes concluidos!" -ForegroundColor Green
Write-Host ""
Write-Host "Proximos passos:" -ForegroundColor Cyan
Write-Host "  1. Acesse a documentacao interativa: $BaseURL/docs" -ForegroundColor White
Write-Host "  2. Verifique os logs: ssh $ServerUser@$ServerIP 'journalctl -u openmind-ai -f'" -ForegroundColor White
Write-Host "  3. Veja logs estruturados: ssh $ServerUser@$ServerIP 'tail -f /var/log/openmind-ai/app.log'" -ForegroundColor White
Write-Host ""

