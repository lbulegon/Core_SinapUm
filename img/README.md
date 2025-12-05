# 🖼️ Imagens de Teste

Esta pasta contém imagens de teste para validação da API de análise do OpenMind AI.

## 📋 Imagens Disponíveis

| Arquivo | Tamanho | Formato | Descrição |
|---------|---------|---------|-----------|
| `teste_rapido.png` | 200x200 | PNG | Imagem pequena para testes rápidos (1.59 KB) |
| `produto_pequeno.jpg` | 400x400 | JPEG | Produto pequeno (12.78 KB) |
| `produto_quadrado.png` | 600x600 | PNG | Produto formato quadrado (7.58 KB) |
| `produto_medio.png` | 800x600 | PNG | Produto tamanho médio (8.18 KB) |
| `produto_retangular.jpg` | 1200x800 | JPEG | Produto formato retangular (39.55 KB) |
| `produto_grande.jpg` | 1600x1200 | JPEG | Produto grande (67.45 KB) |
| `produto_limite.jpg` | 2048x1536 | JPEG | Produto no limite de dimensão (95.61 KB) |

## 🧪 Como Usar

### Via PowerShell (Windows)

```powershell
# Teste rápido com imagem pequena
curl -X POST "http://69.169.102.84:8000/api/v1/analyze" `
  -F "image=@img\teste_rapido.png"

# Teste com imagem média
curl -X POST "http://69.169.102.84:8000/api/v1/analyze" `
  -F "image=@img\produto_medio.png"

# Teste com imagem grande
curl -X POST "http://69.169.102.84:8000/api/v1/analyze" `
  -F "image=@img\produto_grande.jpg"

# Usando o script de testes
.\TESTAR_SERVIDOR.ps1 -TestImage "img\produto_pequeno.jpg"
```

### Via cURL (Linux/Mac)

```bash
# Teste rápido
curl -X POST "http://69.169.102.84:8000/api/v1/analyze" \
  -F "image=@img/teste_rapido.png"

# Teste com diferentes imagens
curl -X POST "http://69.169.102.84:8000/api/v1/analyze" \
  -F "image=@img/produto_medio.png"
```

### Via Swagger UI

1. Acesse: `http://69.169.102.84:8000/docs`
2. Clique em `POST /api/v1/analyze`
3. Clique em "Try it out"
4. Clique em "Choose File" e selecione uma imagem da pasta `img`
5. Clique em "Execute"

### Via Python

```python
import requests

url = "http://69.169.102.84:8000/api/v1/analyze"

# Testar diferentes imagens
imagens = [
    "img/teste_rapido.png",
    "img/produto_pequeno.jpg",
    "img/produto_medio.png",
    "img/produto_grande.jpg"
]

for imagem in imagens:
    with open(imagem, 'rb') as f:
        files = {'image': f}
        response = requests.post(url, files=files)
        print(f"\n{imagem}:")
        print(response.json())
```

## ✅ Casos de Teste

### 1. Teste de Formato JPEG
```bash
curl -X POST "http://69.169.102.84:8000/api/v1/analyze" \
  -F "image=@img/produto_pequeno.jpg"
```

### 2. Teste de Formato PNG
```bash
curl -X POST "http://69.169.102.84:8000/api/v1/analyze" \
  -F "image=@img/produto_medio.png"
```

### 3. Teste de Imagem Pequena (< 1MB)
```bash
curl -X POST "http://69.169.102.84:8000/api/v1/analyze" \
  -F "image=@img/teste_rapido.png"
```

### 4. Teste de Imagem Grande (< 10MB)
```bash
curl -X POST "http://69.169.102.84:8000/api/v1/analyze" \
  -F "image=@img/produto_grande.jpg"
```

### 5. Teste de Dimensão Máxima (2048px)
```bash
curl -X POST "http://69.169.102.84:8000/api/v1/analyze" \
  -F "image=@img/produto_limite.jpg"
```

## 📊 Verificar Tamanho das Imagens

```powershell
# Windows PowerShell
Get-ChildItem img -File | Select-Object Name, @{Name="Size(KB)";Expression={[math]::Round($_.Length/1KB,2)}}, @{Name="Dimensions";Expression={"N/A"}}

# Linux/Mac
ls -lh img/
```

## 🔄 Recriar Imagens

Se precisar recriar as imagens de teste:

```powershell
.\criar_imagens_teste.ps1
```

## 📝 Notas

- Todas as imagens foram criadas automaticamente
- As imagens contêm texto indicando "PRODUTO X" para identificação
- Formatos suportados: JPEG, PNG
- Tamanho máximo: 10 MB
- Dimensão máxima: 2048px (largura ou altura)

