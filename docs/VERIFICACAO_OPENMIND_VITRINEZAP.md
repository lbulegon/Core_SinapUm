# Verificação e Correção do Serviço Openmind para Vitrinezap

## Data: 2024-12-14

## Problemas Identificados

1. **Porta incorreta no Django**: O Django estava configurado para usar a porta 8000, mas o Openmind foi movido para a porta 8001
2. **Endpoint incompatível**: O Django chama `/api/v1/analyze-product-image`, mas o Openmind tinha apenas `/api/v1/analyze`
3. **MEDIA_HOST com porta incorreta**: O código do Openmind estava usando porta 8000 como padrão no MEDIA_HOST

## Correções Realizadas

### 1. Atualização do Django (settings.py)
- ✅ Alterado `OPENMIND_AI_URL` de `http://127.0.0.1:8000` para `http://127.0.0.1:8001`

**Arquivo**: `/root/MCP_SinapUm/setup/settings.py`
```python
OPENMIND_AI_URL = os.environ.get('OPENMIND_AI_URL', 'http://127.0.0.1:8001')
```

### 2. Criação de Endpoint de Compatibilidade no Openmind
- ✅ Criado endpoint `/api/v1/analyze-product-image` no Openmind para manter compatibilidade com o Django
- ✅ O endpoint aceita tanto `image` quanto `images` no form-data
- ✅ Retorna formato compatível com o esperado pelo Django

**Arquivo**: `/root/MCP_SinapUm/services/openmind_service/app/api/v1/endpoints/analyze.py`

### 3. Correção do MEDIA_HOST no Openmind
- ✅ Alterado para usar dinamicamente a porta configurada (`settings.OPENMIND_AI_PORT`)
- ✅ Agora usa `http://localhost:8001` por padrão (ou a porta configurada)

**Arquivo**: `/root/MCP_SinapUm/services/openmind_service/app/api/v1/endpoints/analyze.py`
```python
media_host = settings.MEDIA_HOST or f"http://localhost:{settings.OPENMIND_AI_PORT}"
```

## Configurações Verificadas

### Openmind Service
- ✅ **Porta**: 8001 (configurada no docker-compose.yml e .env)
- ✅ **Container**: `openmind_service` está rodando e saudável
- ✅ **Health Check**: `http://localhost:8001/health` respondendo corretamente
- ✅ **MEDIA_HOST**: Configurado como `http://localhost:8001` no .env

### Django
- ✅ **OPENMIND_AI_URL**: Configurado para `http://127.0.0.1:8001`
- ✅ **Serviço de análise**: Usa `analyze_image_with_openmind()` que chama `/api/v1/analyze-product-image`

## Endpoints Disponíveis no Openmind

1. **POST `/api/v1/analyze`** - Endpoint principal de análise
2. **POST `/api/v1/analyze-product-image`** - Endpoint de compatibilidade para Django/Vitrinezap
3. **GET `/api/v1/analyze/status`** - Status do serviço
4. **GET `/health`** - Health check
5. **GET `/docs`** - Documentação Swagger

## Próximos Passos

### Para aplicar as mudanças:

1. **Reconstruir o container do Openmind** (se necessário):
```bash
cd /root/MCP_SinapUm/services/openmind_service
docker-compose down
docker-compose build
docker-compose up -d
```

2. **Verificar se o Django está usando a nova configuração**:
   - O Django pode precisar ser reiniciado se estiver usando cache de configurações
   - Verificar variável de ambiente `OPENMIND_AI_URL` se estiver usando Docker

3. **Testar a integração**:
```bash
# Testar health check do Openmind
curl http://localhost:8001/health

# Testar endpoint de compatibilidade (requer imagem)
curl -X POST http://localhost:8001/api/v1/analyze-product-image \
  -F "image=@/caminho/para/imagem.jpg"
```

## Status Atual

- ✅ Openmind rodando na porta 8001
- ✅ Django configurado para usar porta 8001
- ✅ Endpoint de compatibilidade criado
- ✅ MEDIA_HOST corrigido
- ⚠️ **Ação necessária**: Reconstruir container do Openmind para aplicar mudanças no código

## Arquivos Modificados

1. `/root/MCP_SinapUm/setup/settings.py` - Porta atualizada para 8001
2. `/root/MCP_SinapUm/services/openmind_service/app/api/v1/endpoints/analyze.py` - Endpoint de compatibilidade adicionado e MEDIA_HOST corrigido

