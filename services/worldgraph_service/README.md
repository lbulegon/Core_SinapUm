# WorldGraph Service (Neo4j)

Serviço de **Memória Diagramática**: grafo heterogêneo dinâmico multicamadas (Property Graph + temporal via Events).

## Descrição

- **Stack**: Neo4j 5
- **Portas**: HTTP `7474` (Browser), BOLT `7687` (drivers)
- **Uso**: Grafo de entidades (Agent, Object, Place, Event) com relações tipadas e camadas (operational, spatial, temporal).

## Variáveis de ambiente

Copie `.env.example` para `.env` e ajuste se necessário:

| Variável | Default | Descrição |
|----------|---------|-----------|
| `WORLDGRAPH_NEO4J_USER` | neo4j | Usuário Neo4j |
| `WORLDGRAPH_NEO4J_PASSWORD` | neo4j12345 | Senha Neo4j |
| `WORLDGRAPH_HTTP_PORT` | 7474 | Porta HTTP (Browser) |
| `WORLDGRAPH_BOLT_PORT` | 7687 | Porta BOLT |
| `WORLDGRAPH_HEAP_INITIAL` | 1G | Heap inicial JVM |
| `WORLDGRAPH_HEAP_MAX` | 1G | Heap máximo JVM |
| `WORLDGRAPH_PAGECACHE` | 1G | Page cache |

## Subir com o monorepo

Na raiz do Core_SinapUm:

```bash
docker compose up -d worldgraph_service
```

Ou junto com o vectorstore:

```bash
docker compose up -d worldgraph_service vectorstore_service
```

## Verificar health

- Browser: `http://localhost:7474` (ou `http://localhost:${WORLDGRAPH_HTTP_PORT}`)
- Login: usuário/senha do `.env` (ex.: neo4j / neo4j12345)

## Popular com seed

1. **Pelo Neo4j Browser** (http://localhost:7474): abra cada arquivo em `seed/` e execute no editor Cypher.
   - Primeiro: `001_schema.cypher` (constraints)
   - Depois: `010_seed.cypher` (nós e arestas)

2. **Pelo cypher-shell** (dentro do container):

```bash
docker exec -i mcp_sinapum_worldgraph cypher-shell -u neo4j -p neo4j12345 < services/worldgraph_service/seed/001_schema.cypher
docker exec -i mcp_sinapum_worldgraph cypher-shell -u neo4j -p neo4j12345 < services/worldgraph_service/seed/010_seed.cypher
```

(Ajuste usuário/senha conforme seu `.env`.)

## Ponte com Vectorstore

O FAISS (vectorstore_service) retorna `id`s; use esses ids para consultar nós no Neo4j (ex.: `MATCH (n {id: $id}) RETURN n`).
