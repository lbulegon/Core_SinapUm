# Variáveis de ambiente — Core_SinapUm (exemplo)

## Celery/Redis
- `CELERY_BROKER_URL=redis://redis:6379/0`
- `CELERY_RESULT_BACKEND=redis://redis:6379/1`

## WhatsApp Gateway (obrigatório para envio real)
- `WHATSAPP_GATEWAY_URL=http://...`  # base URL do gateway (ex.: http://127.0.0.1:8004)
- `SINAPUM_WHATSAPP_GATEWAY_API_KEY=...`  # opcional
- `WHATSAPP_GATEWAY_TIMEOUT=6`

## MCP Evora (opcional; se não setado, usa fallback)
- `EVORA_MCP_URL=...`
- `EVORA_MCP_TOKEN=...`

## Semantic cache
- `SEMANTIC_CACHE_ENABLED=false`  # true para ativar
- `SEMANTIC_EMBEDDINGS_PROVIDER=local`  # ou openai
- `SEMANTIC_LOCAL_MODEL=all-MiniLM-L6-v2`
- `SEMANTIC_VECTOR_DIM=384`
- `SEMANTIC_CACHE_THRESHOLD=0.86`
- `SEMANTIC_CACHE_TOPK=3`
- `REDISVL_INDEX_NAME=vz_semantic_cache`
- `REDISVL_PREFIX=vz:cache`
