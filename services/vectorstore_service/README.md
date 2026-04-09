# Vectorstore Service (FastAPI + FAISS)

Serviço de **Memória Semântica**: vetorização local persistente com FAISS e SentenceTransformers.

## Descrição

- **Stack**: FastAPI, FAISS (IndexFlatIP), SentenceTransformers (all-MiniLM-L6-v2)
- **Porta**: `8010`
- **Persistência**: volume em `/data` (index.faiss + id_map.json)

## Variáveis de ambiente

Copie `.env.example` para `.env` e ajuste se necessário:

| Variável | Default | Descrição |
|----------|---------|-----------|
| `VECTORSTORE_PORT` | 8010 | Porta HTTP da API |
| `VECTORSTORE_DATA_DIR` | /data | Diretório de persistência no container |
| `VECTORSTORE_MODEL` | all-MiniLM-L6-v2 | Modelo SentenceTransformers |

## Subir com o monorepo

Na raiz do Core_SinapUm:

```bash
docker compose up -d vectorstore_service
```

Ou junto com o worldgraph:

```bash
docker compose up -d worldgraph_service vectorstore_service
```

## Verificar health

```bash
curl http://localhost:8010/health
# ou http://localhost:${VECTORSTORE_PORT}/health
```

Resposta esperada: `{"ok": true}`

## Endpoints

### POST /upsert

Inserir ou anexar documento (MVP: append apenas).

```bash
curl -X POST http://localhost:8010/upsert \
  -H "Content-Type: application/json" \
  -d '{"id": "pedido_100", "text": "Pedido aguardando aprovação do restaurante Mister Dog"}'
```

### POST /search

Busca semântica por texto.

```bash
curl -X POST http://localhost:8010/search \
  -H "Content-Type: application/json" \
  -d '{"text": "pedido aguardando", "k": 5}'
```

Resposta: `{"results": [{"id": "pedido_100", "score": 0.85}, ...]}`

## Ponte com WorldGraph (Neo4j)

1. Faça `POST /search` no vectorstore com o texto da consulta.
2. Use os `id`s retornados para consultar o Neo4j, ex.: `MATCH (n {id: $id}) RETURN n`.

Exemplo de fluxo manual: FAISS retorna id → consulta no Neo4j por id para obter o nó completo.
