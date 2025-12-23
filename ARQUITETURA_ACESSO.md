# Arquitetura de Acesso - MCP_SinapUm

## Resposta à Pergunta

**Sim, você poderá acessar o serviço tanto pela porta 8001 quanto pela porta 5000**, mas de formas diferentes:

### Porta 8001 - Acesso Direto ao OpenMind AI
- **URL:** `http://69.169.102.84:8001/api/v1/analyze-product-image`
- **O que é:** Acesso direto ao servidor FastAPI (OpenMind AI)
- **Vantagens:** 
  - Mais rápido (sem intermediário)
  - Acesso direto a todos os endpoints do OpenMind AI
  - Útil para testes e desenvolvimento

### Porta 5000 - Acesso através do Django (MCP_SinapUm)
- **URL:** `http://69.169.102.84:5000/api/v1/analyze-product-image`
- **O que é:** Acesso através do Django que faz proxy/redirecionamento para o OpenMind AI
- **Vantagens:**
  - Integração com banco de dados Django
  - Pode salvar resultados automaticamente
  - Pode adicionar lógica de negócio adicional
  - Acesso unificado através do MCP

## Arquitetura

```
Cliente
  │
  ├─→ Porta 5000 (Django/MCP_SinapUm)
  │     │
  │     ├─→ Salva imagem em /media/uploads/
  │     ├─→ Chama OpenMind AI (interno)
  │     └─→ Retorna resposta com dados + URLs
  │
  └─→ Porta 8001 (OpenMind AI - FastAPI)
        │
        └─→ Analisa imagem e retorna JSON
```

## Configuração do Docker Compose

O `docker-compose.yml` está **correto** - todos os serviços estão na mesma rede:

```yaml
networks:
  - mcp_network  # Todos os serviços usam esta rede
```

### Serviços:
1. **db** (PostgreSQL) - Porta 5432
2. **openmind** (OpenMind AI) - Porta 8001
3. **web** (Django) - Porta 5000

## Como Funciona Internamente

### Quando você acessa pela porta 5000:

1. Cliente faz requisição para `http://69.169.102.84:5000/api/v1/analyze-product-image`
2. Django recebe a requisição em `app_sinapum/views.py::api_analyze_product_image()`
3. Django salva a imagem em `/app/media/uploads/`
4. Django chama o OpenMind AI internamente usando `http://openmind:8001/api/v1/analyze-product-image`
5. Django recebe a resposta do OpenMind AI
6. Django adiciona informações adicionais (image_url, image_path, etc.)
7. Django retorna a resposta completa para o cliente

### Quando você acessa pela porta 8001:

1. Cliente faz requisição para `http://69.169.102.84:8001/api/v1/analyze-product-image`
2. FastAPI (OpenMind AI) recebe diretamente
3. FastAPI analisa a imagem
4. FastAPI retorna a resposta JSON

## Variáveis de Ambiente

### No Django (porta 5000):
```bash
OPENMIND_AI_URL=http://openmind:8001  # Nome do serviço na rede Docker
```

### No OpenMind AI (porta 8001):
```bash
OPENMIND_AI_HOST=0.0.0.0
OPENMIND_AI_PORT=8001
```

## Testando os Endpoints

### Teste 1: Porta 5000 (através do Django)
```bash
curl -X POST http://69.169.102.84:5000/api/v1/analyze-product-image \
  -F "image=@test_image.jpg" \
  -F "language=pt-BR"
```

### Teste 2: Porta 8001 (direto no OpenMind AI)
```bash
curl -X POST http://69.169.102.84:8001/api/v1/analyze-product-image \
  -F "image=@test_image.jpg" \
  -F "language=pt-BR"
```

## Diferenças nas Respostas

### Porta 5000 (Django):
- Inclui `image_url` e `image_path` (URLs geradas pelo Django)
- Pode incluir dados salvos no banco
- Pode ter lógica adicional de processamento

### Porta 8001 (OpenMind AI):
- Resposta direta do FastAPI
- Apenas dados da análise
- Mais rápido (sem overhead do Django)

## Recomendação

- **Para produção/ÉVORA:** Use a porta 5000 (Django) para ter integração completa
- **Para testes/debug:** Use a porta 8001 (OpenMind AI) para acesso direto

## Nota sobre Rede Docker

Se o container `openmind` não conseguir resolver o nome na rede, verifique:

```bash
# Verificar se está na rede
docker network inspect mcp_sinapum_mcp_network

# Conectar manualmente se necessário
docker network connect mcp_sinapum_mcp_network mcp_sinapum_openmind
```

