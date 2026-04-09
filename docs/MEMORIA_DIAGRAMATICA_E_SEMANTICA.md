# Memória Diagramática + Memória Semântica (MVP)

Documentação do MVP de **Memória Diagramática** (Neo4j) e **Memória Semântica** (FAISS) implementado no monorepo Core_SinapUm.

---

## 1. Objetivo

Oferecer dois serviços complementares para agentes e LLMs:

| Componente | Serviço | Função |
|------------|---------|--------|
| **Memória Diagramática** | WorldGraph (Neo4j) | Grafo heterogêneo dinâmico multicamadas: entidades (Agent, Object, Place, Event) e relações com camadas (operational, spatial, temporal). |
| **Memória Semântica** | Vectorstore (FastAPI + FAISS) | Índice vetorial local persistente: busca por similaridade de texto (embedding + FAISS). |

A tríade de uso é: **LLM fala → Grafo lembra (estrutura) → Vetor associa (busca por significado)**. O vetor retorna `id`s que podem ser usados para consultar o grafo no Neo4j.

---

## 2. Arquitetura

```
                    ┌─────────────────────────────────────────────────────────┐
                    │                    Core_SinapUm                         │
                    │                                                         │
  Agente/LLM        │   ┌──────────────────┐      ┌─────────────────────────┐ │
  (texto/intenção)   │   │ vectorstore_    │      │ worldgraph_             │ │
       │            │   │ service         │      │ service                 │ │
       │            │   │ (FastAPI+FAISS)  │      │ (Neo4j 5)               │ │
       ├────────────┼──►│ POST /upsert    │      │ Property Graph          │ │
       │            │   │ POST /search    │      │ + Events (temporal)      │ │
       │            │   │ GET  /health    │      │ Browser: 7474, BOLT:7687 │ │
       │            │   │ Porta: 8010     │      │                         │ │
       │            │   └────────┬────────┘      └────────────┬──────────────┘ │
       │            │            │                            │               │
       │            │            │ ids retornados              │ MATCH (n      │
       │            │            └────────────────────────────┼ {id:$id})     │
       │            │                 ponte (consulta Neo4j)  │               │
       │            │                                          │               │
                    │   Volumes: vectorstore_data              worldgraph_data │
                    │            worldgraph_logs                               │
                    └─────────────────────────────────────────────────────────┘
```

- **vectorstore_service**: persiste `index.faiss` e `id_map.json` em volume; embeddings com SentenceTransformers (all-MiniLM-L6-v2), índice IndexFlatIP (cosine via vetores normalizados).
- **worldgraph_service**: persiste dados e logs do Neo4j em volumes; schema e seed em `services/worldgraph_service/seed/`.

Ambos usam a rede `mcp_network` e seguem o padrão de nomes dos containers (`mcp_sinapum_*`).

---

## 3. Serviço 1: WorldGraph (Neo4j) — Memória Diagramática

### 3.1 Descrição

- **Imagem**: `neo4j:5`
- **Container**: `mcp_sinapum_worldgraph`
- **Portas**: HTTP `7474` (Browser), BOLT `7687` (drivers)
- **Papel**: Grafo de conhecimento com nós tipados (Agent, Object, Place, Event) e relações com atributos `layer` e `ts` (temporal).

### 3.2 Variáveis de ambiente

| Variável | Default | Descrição |
|----------|---------|-----------|
| `WORLDGRAPH_NEO4J_USER` | neo4j | Usuário Neo4j |
| `WORLDGRAPH_NEO4J_PASSWORD` | neo4j12345 | Senha Neo4j |
| `WORLDGRAPH_HTTP_PORT` | 7474 | Porta HTTP (Browser) |
| `WORLDGRAPH_BOLT_PORT` | 7687 | Porta BOLT |
| `WORLDGRAPH_HEAP_INITIAL` | 1G | Heap inicial JVM |
| `WORLDGRAPH_HEAP_MAX` | 1G | Heap máximo JVM |
| `WORLDGRAPH_PAGECACHE` | 1G | Page cache |

Definidas em `Core_SinapUm/.env` (ou `.env.example` na raiz) e em `services/worldgraph_service/.env.example`.

### 3.3 Volumes

- `worldgraph_data` → `/data`
- `worldgraph_logs` → `/logs`
- `./services/worldgraph_service/seed` → `/seed:ro` (somente leitura)

### 3.4 Schema e seed (Cypher)

- **`seed/001_schema.cypher`**: constraints `UNIQUE` para `Agent`, `Object`, `Place`, `Event` no atributo `id`.
- **`seed/010_seed.cypher`**: nós de exemplo (motoboy, restaurante, pedido, lugar) e relações com `layer` e `ts`; um nó `Event` com relação `ABOUT` para o pedido.

### 3.5 Como subir e verificar

```bash
# Na raiz do Core_SinapUm
docker compose up -d worldgraph_service
```

- **Health**: abrir no browser `http://localhost:7474` (ou `http://localhost:${WORLDGRAPH_HTTP_PORT}`). Login com usuário/senha do `.env`.
- **Seed pelo cypher-shell** (executar na raiz do repositório):

```bash
docker exec -i mcp_sinapum_worldgraph cypher-shell -u neo4j -p neo4j12345 < services/worldgraph_service/seed/001_schema.cypher
docker exec -i mcp_sinapum_worldgraph cypher-shell -u neo4j -p neo4j12345 < services/worldgraph_service/seed/010_seed.cypher
```

(Ajuste `-u` e `-p` conforme seu `.env`.)

Documentação detalhada do serviço: **`services/worldgraph_service/README.md`**.

---

## 4. Serviço 2: Vectorstore (FastAPI + FAISS) — Memória Semântica

### 4.1 Descrição

- **Build**: `./services/vectorstore_service` (Dockerfile Python 3.11)
- **Container**: `mcp_sinapum_vectorstore`
- **Porta**: `8010`
- **Papel**: API para upsert (id + texto → embedding no índice) e search (texto → top-k ids por similaridade). Persistência em `/data` (volume `vectorstore_data`).

### 4.2 Variáveis de ambiente

| Variável | Default | Descrição |
|----------|---------|-----------|
| `VECTORSTORE_PORT` | 8010 | Porta HTTP da API |
| `VECTORSTORE_DATA_DIR` | /data | Diretório de persistência no container |
| `VECTORSTORE_MODEL` | all-MiniLM-L6-v2 | Modelo SentenceTransformers |

Definidas em `Core_SinapUm/.env` e em `services/vectorstore_service/.env.example`.

### 4.3 Volumes

- `vectorstore_data` → `/data` (contém `index.faiss` e `id_map.json`)

### 4.4 API

| Método | Endpoint | Descrição |
|--------|----------|-----------|
| GET | `/health` | Health check → `{"ok": true}` |
| POST | `/upsert` | Body: `{"id": "<string>", "text": "<string>"}` — adiciona documento ao índice (MVP: append). |
| POST | `/search` | Body: `{"text": "<string>", "k": <int>}` (k default 5) — retorna `{"results": [{"id": "...", "score": <float>}, ...]}`. |

### 4.5 Como subir e verificar

```bash
# Na raiz do Core_SinapUm
docker compose up -d vectorstore_service
```

- **Health**:

```bash
curl http://localhost:8010/health
# Esperado: {"ok":true}
```

- **Upsert**:

```bash
curl -X POST http://localhost:8010/upsert \
  -H "Content-Type: application/json" \
  -d '{"id": "pedido_100", "text": "Pedido aguardando aprovação do restaurante Mister Dog"}'
```

- **Search**:

```bash
curl -X POST http://localhost:8010/search \
  -H "Content-Type: application/json" \
  -d '{"text": "pedido aguardando", "k": 5}'
```

Documentação detalhada do serviço: **`services/vectorstore_service/README.md`**.

---

## 5. Ponte: Vectorstore → WorldGraph

Fluxo típico para um agente ou LLM:

1. **Busca semântica**: `POST /search` no vectorstore com o texto da pergunta ou contexto.
2. **Resposta**: lista de `{ "id": "...", "score": ... }`.
3. **Enriquecimento no grafo**: usar cada `id` em uma consulta Cypher no Neo4j para obter o nó completo e suas relações.

Exemplo Cypher (Neo4j Browser ou driver):

```cypher
MATCH (n {id: $id}) RETURN n
-- ou com relações
MATCH (n {id: $id}) OPTIONAL MATCH (n)-[r]-(m) RETURN n, r, m
```

Assim, o **vetor** resolve “o que é semanticamente próximo” e o **grafo** fornece a estrutura (entidades e eventos) associada a cada `id`.

---

## 6. Subir os dois serviços juntos

Na raiz do Core_SinapUm:

```bash
docker compose up -d worldgraph_service vectorstore_service
```

Verificação rápida:

- Neo4j: `http://localhost:7474`
- Vectorstore: `curl http://localhost:8010/health`

O `docker compose up -d` completo do monorepo continua funcionando; esses dois serviços são opcionais e não quebram os demais.

---

## 6.1 Como testar os novos serviços

### Script automático (recomendado)

Na raiz do Core_SinapUm:

```bash
# Com containers já rodando
./scripts/test_memoria_services.sh

# Subir os dois serviços e depois testar
./scripts/test_memoria_services.sh --up
```

O script verifica: Neo4j respondendo na porta HTTP, Vectorstore `/health`, `POST /upsert` e `POST /search`, e que o id inserido aparece na busca.

### Testes manuais

1. **Subir os serviços**
   ```bash
   cd /root/Core_SinapUm
   docker compose up -d worldgraph_service vectorstore_service
   ```

2. **WorldGraph (Neo4j)**  
   - Abrir no browser: `http://localhost:7474` (login ex.: neo4j / neo4j12345).  
   - Popular com seed (opcional):
     ```bash
     docker exec -i mcp_sinapum_worldgraph cypher-shell -u neo4j -p neo4j12345 < services/worldgraph_service/seed/001_schema.cypher
     docker exec -i mcp_sinapum_worldgraph cypher-shell -u neo4j -p neo4j12345 < services/worldgraph_service/seed/010_seed.cypher
     ```

3. **Vectorstore**
   ```bash
   curl http://localhost:8010/health
   curl -X POST http://localhost:8010/upsert -H "Content-Type: application/json" -d '{"id":"pedido_100","text":"Pedido aguardando aprovação"}'
   curl -X POST http://localhost:8010/search -H "Content-Type: application/json" -d '{"text":"pedido aguardando","k":5}'
   ```

4. **Ponte (manual)**  
   Use um `id` retornado por `/search` no Neo4j Browser: `MATCH (n {id: "pedido_100"}) RETURN n`.

**Se `docker compose ps` travar:** use o Docker diretamente (resposta imediata):
```bash
docker ps -a | grep -E 'worldgraph|vectorstore'
```
Nomes dos containers: `mcp_sinapum_worldgraph`, `mcp_sinapum_vectorstore`.

**Se `docker compose restart` travar** (muitos containers): use o script que reinicia por nome, sem Compose:
```bash
cd /root/Core_SinapUm
./scripts/restart_core_containers.sh                                    # todos
./scripts/restart_core_containers.sh mcp_sinapum_vectorstore mcp_sinapum_worldgraph   # só memória
```

**Subir um a um** (evita travar ao iniciar tudo de uma vez):
```bash
cd /root/Core_SinapUm
./scripts/start_core_containers.sh           # inicia na ordem de dependência, com pausa de 2s entre cada
./scripts/start_core_containers.sh --no-wait # sem pausa
```

---

## 7. Estrutura de arquivos (implementação)

```
Core_SinapUm/
├── docker-compose.yml                    # Inclui worldgraph_service e vectorstore_service + volumes
├── .env.example                          # Variáveis WORLDGRAPH_* e VECTORSTORE_*
├── docs/
│   └── MEMORIA_DIAGRAMATICA_E_SEMANTICA.md   # Este documento
└── services/
    ├── worldgraph_service/
    │   ├── .env.example
    │   ├── docker-compose.service.yml    # Compose standalone do serviço
    │   ├── README.md
    │   └── seed/
    │       ├── 001_schema.cypher
    │       └── 010_seed.cypher
    └── vectorstore_service/
        ├── .env.example
        ├── docker-compose.service.yml
        ├── Dockerfile
        ├── README.md
        ├── requirements.txt
        └── app/
            ├── __init__.py
            ├── main.py
            └── faiss_store.py
```

---

## 8. Resumo de referências

| Tópico | Onde ver |
|--------|----------|
| **Testar os dois serviços** | `./scripts/test_memoria_services.sh` ou `./scripts/test_memoria_services.sh --up` |
| WorldGraph (Neo4j) — uso e seed | `services/worldgraph_service/README.md` |
| Vectorstore (FAISS) — API e exemplos | `services/vectorstore_service/README.md` |
| Variáveis de ambiente (raiz) | `Core_SinapUm/.env.example` |
| Compose principal | `Core_SinapUm/docker-compose.yml` (blocos `worldgraph_service` e `vectorstore_service`) |

---

## 9. Observações técnicas (MVP)

- **FAISS**: único uso de FAISS no Core_SinapUm é o vectorstore_service; não há outro índice vetorial a unificar.
- **Vectorstore**: upsert em modo append (sem update por id neste MVP); índice `IndexFlatIP` com embeddings normalizados (equivalente a cosine).
- **Neo4j**: sem dependências entre serviços; worldgraph e vectorstore não dependem de outros containers para subir.
- **Licenças**: stack 100% open-source (Neo4j Community, FastAPI, FAISS, SentenceTransformers, etc.).
