# 🔧 Endpoint API REST para Upload e Análise de Imagens

## 📋 Resumo das Modificações

Foi criado um endpoint API REST no SinapUm que:
1. **Recebe imagens** via POST (form-data)
2. **Salva as imagens** no servidor SinapUm (não no Railway)
3. **Retorna a URL completa** da imagem salva no campo `image_url` da resposta JSON

Isso permite que o projeto Évora (Railway) envie imagens diretamente para o SinapUm, sem salvar localmente.

---

## 🚀 Endpoint Criado

### `POST /api/v1/analyze-product-image`

**Localização:** `app_sinapum/views.py` → função `api_analyze_product_image()`

**Rota:** Adicionada em `setup/urls.py`

**Método:** POST

**Content-Type:** `multipart/form-data`

**Campos aceitos:**
- `image` (arquivo) - Arquivo de imagem único
- `images` (arquivo[]) - Múltiplos arquivos (usa a primeira)

---

## 📤 Formato da Requisição

```bash
curl -X POST "http://69.169.102.84:5000/api/v1/analyze-product-image" \
  -F "image=@caminho/para/imagem.jpg"
```

**Com autenticação (se necessário):**
```bash
curl -X POST "http://69.169.102.84:5000/api/v1/analyze-product-image" \
  -H "Authorization: Bearer TOKEN" \
  -F "image=@caminho/para/imagem.jpg"
```

---

## 📥 Formato da Resposta

### Sucesso (200 OK)

```json
{
  "success": true,
  "data": {
    "produto": {
      "nome": "Nome do Produto",
      "marca": "Marca",
      "descricao": "Descrição...",
      "categoria": "Categoria",
      "subcategoria": "Subcategoria",
      "codigo_barras": "1234567890123",
      "imagens": [
        "media/uploads/uuid.jpg"
      ]
    },
    "produto_generico_catalogo": { ... },
    "produto_viagem": { ... },
    "estabelecimento": { ... },
    "campanha": { ... },
    "shopper": { ... },
    "cadastro_meta": { ... }
  },
  "image_url": "http://69.169.102.84:5000/media/uploads/uuid.jpg",
  "image_path": "media/uploads/uuid.jpg",
  "saved_filename": "uuid.jpg"
}
```

### Erro (400/500)

```json
{
  "success": false,
  "error": "Mensagem de erro",
  "error_code": "NO_IMAGE" | "INVALID_FILE_TYPE" | "INTERNAL_ERROR"
}
```

---

## 🔑 Campos Importantes na Resposta

| Campo | Tipo | Descrição |
|-------|------|-----------|
| `image_url` | string | **URL completa e acessível** da imagem salva no SinapUm (ex: `http://69.169.102.84:5000/media/uploads/uuid.jpg`) |
| `image_path` | string | Caminho relativo da imagem (ex: `media/uploads/uuid.jpg`) - usado no JSON do produto |
| `saved_filename` | string | Nome do arquivo salvo (ex: `uuid.jpg`) |
| `data.produto.imagens[]` | array | Array contendo o caminho relativo da imagem |

---

## 📁 Localização das Imagens Salvas

**Diretório físico:** `{BASE_DIR}/media/uploads/`

**URL pública:** `http://69.169.102.84:5000/media/uploads/{uuid}.{ext}`

**Exemplo:**
- Arquivo: `/root/SinapUm/media/uploads/39cc7cc8-f610-422a-8949-c28e181473e4.jpg`
- URL: `http://69.169.102.84:5000/media/uploads/39cc7cc8-f610-422a-8949-c28e181473e4.jpg`

---

## 🔄 Fluxo Completo

1. **Évora (Railway)** envia imagem via POST para `/api/v1/analyze-product-image`
2. **SinapUm** recebe a imagem e:
   - Valida o tipo de arquivo
   - Gera um nome único (UUID)
   - Salva em `media/uploads/{uuid}.{ext}`
   - Analisa a imagem com OpenMind AI
   - Retorna resposta JSON com `image_url` completa
3. **Évora** recebe a resposta e:
   - Usa `image_url` para exibir/armazenar referência à imagem
   - Não precisa salvar localmente (não tem mais 404)

---

## 🛠️ Modificações Realizadas

### 1. Nova View API (`app_sinapum/views.py`)

**Função:** `api_analyze_product_image(request)`

**Funcionalidades:**
- ✅ Validação de tipo de arquivo
- ✅ Salvamento de imagem com UUID único
- ✅ Geração de URL completa (`http://host:port/media/uploads/uuid.jpg`)
- ✅ Análise com OpenMind AI
- ✅ Retorno de `image_url`, `image_path` e `saved_filename`
- ✅ Inclusão do caminho da imagem no JSON do produto

### 2. Atualização de `services.py`

**Função:** `analyze_image_with_openmind(image_file, image_path=None, image_url=None)`

**Mudanças:**
- Adicionados parâmetros opcionais `image_path` e `image_url`
- Passa `image_path` para `transform_evora_to_modelo_json()`
- Inclui `image_url` e `image_path` na resposta JSON

### 3. Atualização de `urls.py`

**Adicionado:**
```python
path('api/v1/analyze-product-image', views.api_analyze_product_image, name='api_analyze_product_image'),
```

**Configuração de mídia:**
- Servir arquivos de mídia em produção (não apenas em DEBUG)

### 4. Views Existentes Atualizadas

**`analyze_image()` e `handle_reanalyze()`:**
- Atualizadas para passar `image_path` e `image_url` para `analyze_image_with_openmind()`
- Mantém compatibilidade com interface web existente

---

## ✅ Checklist de Implementação

- [x] Endpoint API REST criado (`/api/v1/analyze-product-image`)
- [x] Salvamento de imagens no servidor SinapUm
- [x] Geração de URL completa (`image_url`)
- [x] Retorno de `image_url` na resposta JSON
- [x] Inclusão do caminho no JSON do produto (`produto.imagens[]`)
- [x] Servir arquivos de mídia publicamente
- [x] Validação de tipo de arquivo
- [x] Tratamento de erros
- [x] Logging para debugging

---

## 🧪 Como Testar

### Teste Manual (curl)

```bash
# Enviar imagem para análise
curl -X POST "http://69.169.102.84:5000/api/v1/analyze-product-image" \
  -F "image=@/caminho/para/imagem.jpg" \
  -H "Content-Type: multipart/form-data"
```

### Teste com Python (requests)

```python
import requests

url = "http://69.169.102.84:5000/api/v1/analyze-product-image"
with open("imagem.jpg", "rb") as f:
    files = {"image": f}
    response = requests.post(url, files=files)
    
result = response.json()
print(f"Image URL: {result.get('image_url')}")
print(f"Image Path: {result.get('image_path')}")
```

---

## 🔍 Verificação

1. **Imagem salva?**
   ```bash
   ls -la /root/SinapUm/media/uploads/
   ```

2. **URL acessível?**
   ```bash
   curl -I http://69.169.102.84:5000/media/uploads/{uuid}.jpg
   # Deve retornar 200 OK
   ```

3. **JSON contém image_url?**
   ```bash
   # Verificar resposta do endpoint
   curl -X POST "http://69.169.102.84:5000/api/v1/analyze-product-image" \
     -F "image=@imagem.jpg" | jq '.image_url'
   ```

---

## 📝 Notas Importantes

1. **CSRF Exempt:** O endpoint usa `@csrf_exempt` para permitir requisições de outros domínios (Évora). Em produção, considere usar autenticação por token.

2. **Armazenamento:** As imagens são salvas em `media/uploads/`. Para produção, considere:
   - Usar S3 ou Google Cloud Storage
   - Configurar nginx para servir arquivos estáticos
   - Implementar limpeza periódica de imagens antigas

3. **Segurança:**
   - Validação de tipo de arquivo (apenas imagens)
   - Nomes únicos (UUID) previnem sobrescrita
   - Limite de tamanho de arquivo (configurar em nginx/Django)

4. **URLs Dinâmicas:** A URL é gerada dinamicamente usando `request.get_host()`, funcionando em diferentes ambientes (dev, prod).

---

## 🚨 Problemas Conhecidos

Nenhum no momento.

---

## 📚 Referências

- Django File Uploads: https://docs.djangoproject.com/en/stable/topics/http/file-uploads/
- Django Media Files: https://docs.djangoproject.com/en/stable/howto/static-files/#serving-uploaded-files-in-development

---

**Data de Criação:** 2025-01-08
**Última Atualização:** 2025-01-08

