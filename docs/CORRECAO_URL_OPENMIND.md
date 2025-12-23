# Correção da URL da API OpenMind.org

## Problema Identificado

O erro mostrava:
```
ERROR: Erro na API OpenMind.org: 404 - {"error":"Root not found!"}
```

Isso indicava que a URL da API estava incorreta.

## Correções Realizadas

### 1. Ajuste da URL Base

**Antes:**
```python
self.base_url = "https://api.openmind.org/api/core/openai/v1"
```

**Agora:**
```python
self.base_url = getattr(settings, 'OPENMIND_ORG_BASE_URL', 'https://api.openmind.org/api/core/openai')
```

### 2. Construção Dinâmica do Endpoint

Agora o código detecta automaticamente o formato da URL e constrói o endpoint correto:

```python
if '/v1' in self.base_url:
    api_url = f"{self.base_url}/chat/completions"
elif self.base_url.endswith('/openai'):
    api_url = f"{self.base_url}/v1/chat/completions"
else:
    api_url = f"{self.base_url}/v1/chat/completions"
```

### 3. Configurações Adicionadas

Adicionadas ao `config.py`:
- `OPENMIND_ORG_BASE_URL`: URL base da API OpenMind.org
- `OPENMIND_ORG_MODEL`: Modelo a ser usado (padrão: gpt-4o)

### 4. Melhor Tratamento de Erros

Agora os erros mostram:
- Status code
- Mensagem de erro detalhada
- URL que foi chamada
- Logs mais informativos

## Configuração no .env

Para configurar via variáveis de ambiente, adicione ao `.env` do Openmind service:

```env
OPENMIND_ORG_BASE_URL=https://api.openmind.org/api/core/openai
OPENMIND_ORG_MODEL=gpt-4o
```

## Teste

Após reconstruir o container, teste com:

```bash
curl -X POST http://localhost:8001/api/v1/analyze-product-image \
  -F "image=@/caminho/para/imagem.jpg"
```

## Próximos Passos

1. Reconstruir o container do Openmind
2. Verificar logs para confirmar a URL sendo usada
3. Testar análise de imagem
4. Se ainda houver erro 404, verificar documentação do OpenMind.org para URL correta

