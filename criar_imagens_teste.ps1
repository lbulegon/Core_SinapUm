# Script para criar imagens de teste para análise do OpenMind AI
# Cria imagens em diferentes formatos e tamanhos

$imgDir = "img"
if (-not (Test-Path $imgDir)) {
    New-Item -ItemType Directory -Path $imgDir | Out-Null
}

Write-Host "Criando imagens de teste..." -ForegroundColor Cyan

# Verificar se System.Drawing está disponível
try {
    Add-Type -AssemblyName System.Drawing
    
    # Função para criar imagem
    function Create-TestImage {
        param(
            [int]$Width,
            [int]$Height,
            [string]$Text,
            [string]$FileName,
            [string]$Format,
            [string]$BgColor = "White"
        )
        
        $bitmap = New-Object System.Drawing.Bitmap($Width, $Height)
        $graphics = [System.Drawing.Graphics]::FromImage($bitmap)
        $graphics.SmoothingMode = [System.Drawing.Drawing2D.SmoothingMode]::AntiAlias
        
        # Preencher fundo
        $bgBrush = [System.Drawing.Brushes]::$BgColor
        if (-not $bgBrush) {
            $bgBrush = [System.Drawing.Brushes]::White
        }
        $graphics.FillRectangle($bgBrush, 0, 0, $Width, $Height)
        
        # Adicionar borda
        $pen = New-Object System.Drawing.Pen([System.Drawing.Color]::Gray, 2)
        $graphics.DrawRectangle($pen, 1, 1, $Width - 3, $Height - 3)
        
        # Adicionar texto
        $font = New-Object System.Drawing.Font("Arial", [Math]::Max(12, $Height / 10), [System.Drawing.FontStyle]::Bold)
        $textBrush = [System.Drawing.Brushes]::Black
        $stringFormat = New-Object System.Drawing.StringFormat
        $stringFormat.Alignment = [System.Drawing.StringAlignment]::Center
        $stringFormat.LineAlignment = [System.Drawing.StringAlignment]::Center
        
        $graphics.DrawString($Text, $font, $textBrush, $Width / 2, $Height / 2, $stringFormat)
        
        # Adicionar linha de produto simulada
        $smallFont = New-Object System.Drawing.Font("Arial", [Math]::Max(8, $Height / 15))
        $graphics.DrawString("PRODUTO TESTE", $smallFont, $textBrush, $Width / 2, $Height - 30, $stringFormat)
        
        # Salvar imagem
        $fullPath = Join-Path $imgDir $FileName
        
        switch ($Format.ToUpper()) {
            "PNG" {
                $bitmap.Save($fullPath, [System.Drawing.Imaging.ImageFormat]::Png)
            }
            "JPEG" {
                $bitmap.Save($fullPath, [System.Drawing.Imaging.ImageFormat]::Jpeg)
            }
            default {
                $bitmap.Save($fullPath, [System.Drawing.Imaging.ImageFormat]::Png)
            }
        }
        
        $graphics.Dispose()
        $bitmap.Dispose()
        
        Write-Host "  Criada: $FileName ($Width x $Height)" -ForegroundColor Green
    }
    
    # Criar imagens de teste
    
    # 1. Imagem pequena JPEG
    Create-TestImage -Width 400 -Height 400 -Text "PRODUTO 1" -FileName "produto_pequeno.jpg" -Format "JPEG" -BgColor "LightBlue"
    
    # 2. Imagem média PNG
    Create-TestImage -Width 800 -Height 600 -Text "PRODUTO 2" -FileName "produto_medio.png" -Format "PNG" -BgColor "LightGreen"
    
    # 3. Imagem grande JPEG
    Create-TestImage -Width 1600 -Height 1200 -Text "PRODUTO 3" -FileName "produto_grande.jpg" -Format "JPEG" -BgColor "LightYellow"
    
    # 4. Imagem quadrada PNG
    Create-TestImage -Width 600 -Height 600 -Text "PRODUTO 4" -FileName "produto_quadrado.png" -Format "PNG" -BgColor "LightCoral"
    
    # 5. Imagem retangular JPEG
    Create-TestImage -Width 1200 -Height 800 -Text "PRODUTO 5" -FileName "produto_retangular.jpg" -Format "JPEG" -BgColor "LightPink"
    
    # 6. Imagem pequena para teste rápido
    Create-TestImage -Width 200 -Height 200 -Text "TESTE" -FileName "teste_rapido.png" -Format "PNG" -BgColor "LightGray"
    
    # 7. Imagem no limite de dimensão (2048px)
    Create-TestImage -Width 2048 -Height 1536 -Text "LIMITE 2048px" -FileName "produto_limite.jpg" -Format "JPEG" -BgColor "LightSteelBlue"
    
    Write-Host "`nImagens criadas com sucesso na pasta 'img'!" -ForegroundColor Green
    Write-Host "`nArquivos criados:" -ForegroundColor Cyan
    Get-ChildItem $imgDir -File | ForEach-Object {
        $sizeKB = [math]::Round($_.Length / 1KB, 2)
        Write-Host "  - $($_.Name) ($sizeKB KB)" -ForegroundColor White
    }
    
} catch {
    Write-Host "`nErro ao criar imagens: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host "`nCriando imagens alternativas usando método simples..." -ForegroundColor Yellow
    
    # Método alternativo: criar arquivos de texto que simulam imagens
    # (Para uso posterior com ferramentas de conversão)
    @"
# Para criar imagens de teste manualmente ou com outra ferramenta:
# Use estas especificações:

produto_pequeno.jpg - 400x400, JPEG
produto_medio.png - 800x600, PNG  
produto_grande.jpg - 1600x1200, JPEG
produto_quadrado.png - 600x600, PNG
produto_retangular.jpg - 1200x800, JPEG
teste_rapido.png - 200x200, PNG
produto_limite.jpg - 2048x1536, JPEG
"@ | Out-File -FilePath "$imgDir\especificacoes.txt" -Encoding UTF8
    
    Write-Host "  Arquivo de especificacoes criado em: $imgDir\especificacoes.txt" -ForegroundColor Yellow
}

