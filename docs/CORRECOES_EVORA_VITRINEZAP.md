# Correções Necessárias no Código Évora/Vitrinezap

## Localização do Código
`C:\Users\lbule\OneDrive\Documentos\Source\evora`

## Correções Necessárias

### 1. URL do Openmind AI
**Problema**: O código provavelmente está apontando para a porta 8000 ou URL antiga.

**Correção necessária**: Atualizar para usar a porta 8001.

**Onde procurar**:
- Arquivos de configuração (`.env`, `config.js`, `settings.py`, etc.)
- Arquivos de serviço/API que fazem chamadas ao Openmind
- Constantes ou variáveis de ambiente

**Valor correto**:
```javascript
// JavaScript/TypeScript
const OPENMIND_AI_URL = 'http://127.0.0.1:8001';
// ou
const OPENMIND_AI_URL = process.env.OPENMIND_AI_URL || 'http://127.0.0.1:8001';
```

```python
# Python
OPENMIND_AI_URL = os.getenv('OPENMIND_AI_URL', 'http://127.0.0.1:8001')
```

```env
# .env
OPENMIND_AI_URL=http://127.0.0.1:8001
```

### 2. Endpoint de Análise de Imagens
**Endpoint correto**: `/api/v1/analyze-product-image`

**URL completa**: `http://127.0.0.1:8001/api/v1/analyze-product-image`

**Exemplo de chamada**:
```javascript
// JavaScript/TypeScript
const response = await fetch('http://127.0.0.1:8001/api/v1/analyze-product-image', {
  method: 'POST',
  headers: {
    // Se necessário, adicionar Authorization
    // 'Authorization': 'Bearer YOUR_API_KEY'
  },
  body: formData // FormData com campo 'image' ou 'images'
});
```

```python
# Python
import requests

url = 'http://127.0.0.1:8001/api/v1/analyze-product-image'
files = {'image': open('imagem.jpg', 'rb')}
response = requests.post(url, files=files)
```

### 3. Formato da Requisição
**Campo de upload**: `image` (ou `images` para múltiplas)

**Content-Type**: `multipart/form-data`

**Exemplo**:
```javascript
const formData = new FormData();
formData.append('image', fileInput.files[0]);
// ou para múltiplas imagens:
// formData.append('images', fileInput.files[0]);
// formData.append('images', fileInput.files[1]);
```

### 4. Formato da Resposta
**Estrutura esperada**:
```json
{
  "success": true,
  "data": {
    "produto": {
      "nome": "...",
      "marca": "...",
      "categoria": "...",
      "codigo_barras": "...",
      "imagens": ["media/uploads/uuid.jpg"]
    },
    "cadastro_meta": {
      "fonte": "..."
    }
  },
  "image_path": "media/uploads/uuid.jpg",
  "image_url": "http://localhost:8001/media/uploads/uuid.jpg",
  "saved_filename": "uuid.jpg"
}
```

### 5. Tratamento de Erros
**Códigos de erro possíveis**:
- `NO_IMAGE`: Nenhuma imagem enviada
- `INVALID_FILE_TYPE`: Tipo de arquivo inválido
- `ANALYSIS_ERROR`: Erro na análise
- `CONNECTION_ERROR`: Erro de conexão
- `API_ERROR`: Erro da API

**Exemplo de tratamento**:
```javascript
try {
  const response = await fetch(url, options);
  const result = await response.json();
  
  if (!result.success) {
    console.error('Erro:', result.error);
    console.error('Código:', result.error_code);
    // Tratar erro
  } else {
    // Processar resultado
    const produto = result.data.produto;
  }
} catch (error) {
  console.error('Erro de conexão:', error);
}
```

## Arquivos que Provavelmente Precisam de Alteração

1. **Arquivos de configuração**:
   - `.env`
   - `config.js` / `config.ts`
   - `settings.py`
   - `constants.js` / `constants.ts`

2. **Serviços/APIs**:
   - `api.js` / `api.ts`
   - `services.js` / `services.ts`
   - `openmindService.js` / `openmindService.ts`
   - Qualquer arquivo que faça chamadas HTTP ao Openmind

3. **Componentes/Views**:
   - Componentes de upload de imagem
   - Views que processam análise de imagens
   - Formulários de cadastro de produtos

## Como Encontrar os Arquivos

### Buscar por padrões:
```bash
# No terminal do Windows (PowerShell ou CMD)
cd C:\Users\lbule\OneDrive\Documentos\Source\evora

# Buscar por referências à porta 8000
findstr /s /i "8000" *.js *.ts *.py *.env *.json

# Buscar por "openmind"
findstr /s /i "openmind" *.js *.ts *.py *.env

# Buscar por "analyze"
findstr /s /i "analyze" *.js *.ts *.py
```

### Arquivos comuns a verificar:
- `src/config/` ou `config/`
- `src/services/` ou `services/`
- `src/api/` ou `api/`
- `.env` ou `.env.local`
- `package.json` (para scripts/configurações)
- `docker-compose.yml` (se usar Docker)

## Checklist de Verificação

- [ ] URL do Openmind atualizada para porta 8001
- [ ] Endpoint correto: `/api/v1/analyze-product-image`
- [ ] Campo de upload: `image` ou `images`
- [ ] Tratamento de erros implementado
- [ ] Formato de resposta tratado corretamente
- [ ] Variáveis de ambiente configuradas (se aplicável)
- [ ] Testes realizados após alterações

## Teste da Integração

Após fazer as correções, teste com:

```bash
# Teste simples com curl
curl -X POST http://127.0.0.1:8001/api/v1/analyze-product-image \
  -F "image=@caminho/para/imagem.jpg"
```

Ou através da interface do Évora/Vitrinezap fazendo upload de uma imagem de produto.

