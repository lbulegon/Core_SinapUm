# Script de Teste Rápido - Envia uma imagem para análise
# Uso: .\TESTE_RAPIDO.ps1 [nome_imagem]

param(
    [string]$Imagem = "img\teste_rapido.png",
    [string]$ServerURL = "http://69.169.102.84:8000"
)

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Teste Rapido - Analise de Imagem" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Verificar se a imagem existe
if (-not (Test-Path $Imagem)) {
    Write-Host "[ERRO] Imagem nao encontrada: $Imagem" -ForegroundColor Red
    Write-Host ""
    Write-Host "Imagens disponiveis:" -ForegroundColor Yellow
    Get-ChildItem img -File | ForEach-Object {
        Write-Host "  - $($_.Name)" -ForegroundColor White
    }
    exit 1
}

$fileInfo = Get-Item $Imagem
$sizeKB = [math]::Round($fileInfo.Length / 1KB, 2)

Write-Host "Imagem: $Imagem" -ForegroundColor White
Write-Host "Tamanho: $sizeKB KB" -ForegroundColor Gray
Write-Host "Servidor: $ServerURL" -ForegroundColor Gray
Write-Host ""

# Fazer requisição
Write-Host "Enviando imagem para analise..." -ForegroundColor Yellow

try {
    $imageBytes = [System.IO.File]::ReadAllBytes($Imagem)
    $boundary = [System.Guid]::NewGuid().ToString()
    $fileContent = [System.Text.Encoding]::GetEncoding('iso-8859-1').GetString($imageBytes)
    $fileName = Split-Path $Imagem -Leaf
    
    $bodyLines = (
        "--$boundary",
        "Content-Disposition: form-data; name=`"image`"; filename=`"$fileName`"",
        "Content-Type: image/$(if ($Imagem -match '\.jpg|\.jpeg') { 'jpeg' } else { 'png' })",
        "",
        $fileContent,
        "--$boundary--"
    )
    $body = $bodyLines -join "`r`n"
    
    $headers = @{
        "Content-Type" = "multipart/form-data; boundary=$boundary"
    }
    
    $stopwatch = [System.Diagnostics.Stopwatch]::StartNew()
    $response = Invoke-WebRequest -Uri "$ServerURL/api/v1/analyze-product-image" -Method POST -Body $body -Headers $headers -TimeoutSec 30 -ErrorAction Stop
    $stopwatch.Stop()
    
    Write-Host "[OK] Requisicao bem-sucedida!" -ForegroundColor Green
    Write-Host "Tempo: $($stopwatch.ElapsedMilliseconds)ms" -ForegroundColor Gray
    Write-Host ""
    Write-Host "Resposta:" -ForegroundColor Cyan
    Write-Host "---------" -ForegroundColor Cyan
    
    try {
        $json = $response.Content | ConvertFrom-Json
        $json | ConvertTo-Json -Depth 10 | Write-Host -ForegroundColor White
    } catch {
        Write-Host $response.Content -ForegroundColor White
    }
    
} catch {
    Write-Host "[ERRO] Falha na requisicao" -ForegroundColor Red
    Write-Host $_.Exception.Message -ForegroundColor Red
    
    if ($_.Exception.Response) {
        $reader = New-Object System.IO.StreamReader($_.Exception.Response.GetResponseStream())
        $responseBody = $reader.ReadToEnd()
        Write-Host ""
        Write-Host "Resposta do servidor:" -ForegroundColor Yellow
        Write-Host $responseBody -ForegroundColor Yellow
    }
}

Write-Host ""

