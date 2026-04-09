# MLflow Tracking Server - Core_SinapUm

## O que e

O **MLflow** e a plataforma open-source de experiment tracking e model registry integrada ao Core_SinapUm. Ele permite:

- **Rastrear experimentos**: logar parametros, metricas e artifacts de treinos de modelos de IA
- **Comparar runs**: visualizar e comparar diferentes configuracoes de modelos na UI web
- **Registrar modelos**: versionar e gerenciar modelos treinados via Model Registry
- **Reprodutibilidade**: garantir que qualquer experimento possa ser reproduzido

## Arquitetura

```
                 +-------------------+
                 |   MLflow UI/API   |
                 |  (porta 5050)     |
                 +--------+----------+
                          |
              +-----------+-----------+
              |                       |
    +---------v---------+   +---------v---------+
    | PostgreSQL         |  | Volume Docker      |
    | (mlflow_postgres)  |  | (mlflow_artifacts) |
    | Backend Store:     |  | Artifact Store:    |
    | runs, metricas,    |  | modelos, arquivos, |
    | parametros         |  | outputs            |
    +--------------------+  +--------------------+
```

- **Backend Store**: PostgreSQL dedicado (`mlflow_postgres`) persiste metadados (experiments, runs, metricas, parametros)
- **Artifact Store**: Volume Docker (`mlflow_artifacts`) persiste arquivos (modelos serializados, plots, outputs)

## Quick Start

### 1. Configurar variaveis de ambiente

```bash
cd services/mlflow_service
cp .env.example .env
# Edite o .env se precisar alterar portas ou credenciais
```

### 2. Subir o servico

```bash
# Da raiz do Core_SinapUm:
docker compose up -d mlflow
```

Isso sobe automaticamente o `mlflow_postgres` (dependencia) e o `mlflow` (tracking server).

### 3. Acessar a UI

Abra no navegador:

```
http://localhost:5050
```

(ou a porta configurada em `MLFLOW_HOST_PORT` no `.env`)

### 4. Verificar saude do servico

```bash
# Healthcheck do MLflow
curl http://localhost:5050/

# Healthcheck do Postgres do MLflow
docker compose exec mlflow_postgres pg_isready -U mlflow_user
```

## Configuracao

### Variaveis de Ambiente

| Variavel | Default | Descricao |
|---|---|---|
| `MLFLOW_HOST_PORT` | `5050` | Porta no host para acessar a UI |
| `MLFLOW_BACKEND_URI` | `postgresql://mlflow_user:mlflow_pass@mlflow_postgres:5432/mlflow_db` | URI do PostgreSQL |
| `MLFLOW_ARTIFACT_ROOT` | `/mlflow/artifacts` | Diretorio de artifacts no container |
| `MLFLOW_TRACKING_URI` | `http://localhost:5050` | URI para clientes Python |
| `MLFLOW_POSTGRES_DB` | `mlflow_db` | Nome do database |
| `MLFLOW_POSTGRES_USER` | `mlflow_user` | Usuario do Postgres |
| `MLFLOW_POSTGRES_PASSWORD` | `mlflow_pass` | Senha do Postgres |

### Postgres

Este servico usa um **PostgreSQL dedicado** (`mlflow_postgres`) para nao interferir no Postgres principal do Core_SinapUm (`db`). O banco e criado automaticamente pelo container.

**Alternativa: Reutilizar o Postgres principal (`db`)**

Se preferir usar o Postgres principal do Core_SinapUm, voce precisa:

1. Criar manualmente o database e user:
```sql
CREATE USER mlflow_user WITH PASSWORD 'mlflow_pass';
CREATE DATABASE mlflow_db OWNER mlflow_user;
```

2. Alterar `MLFLOW_BACKEND_URI` no `.env`:
```
MLFLOW_BACKEND_URI=postgresql://mlflow_user:mlflow_pass@db:5432/mlflow_db
```

3. Alterar `depends_on` no `docker-compose.yml` de `mlflow_postgres` para `db`.

## Rodar Exemplos

### Pre-requisitos (local)

```bash
cd services/mlflow_service
pip install -r requirements.txt
```

### Exemplo 1: Logar Experiment

```bash
export MLFLOW_TRACKING_URI=http://localhost:5050
python client_examples/quickstart_log_experiment.py
```

Loga parametros, metricas (10 epochs) e um artifact de texto no experimento `core_sinapum_playground`.

### Exemplo 2: Logar Modelo Sklearn

```bash
export MLFLOW_TRACKING_URI=http://localhost:5050
python client_examples/quickstart_log_model.py
```

Treina um LogisticRegression no dataset Iris, registra o modelo no MLflow Model Registry e loga metricas de accuracy, F1, precision e recall.

### Exemplo 3: Usar de dentro de outro container

De qualquer outro servico Docker na rede `mcp_network`:

```python
import mlflow
mlflow.set_tracking_uri("http://mlflow:5000")
mlflow.set_experiment("meu_experimento")

with mlflow.start_run():
    mlflow.log_param("param1", "valor")
    mlflow.log_metric("metrica1", 0.95)
```

Note que dentro da rede Docker, a URI e `http://mlflow:5000` (nome do servico + porta interna).

## Persistencia

| Dado | Onde | Volume Docker |
|---|---|---|
| Metadados (runs, metricas, parametros) | PostgreSQL (`mlflow_postgres`) | `mlflow_postgres_data` |
| Artifacts (modelos, arquivos) | `/mlflow/artifacts` | `mlflow_artifacts` |

Os dados sobrevivem a `docker compose down`. Para resetar completamente:

```bash
docker compose down -v  # CUIDADO: remove TODOS os volumes do compose
# Ou remover apenas os volumes do MLflow:
docker volume rm core_sinapum_mlflow_postgres_data core_sinapum_mlflow_artifacts
```

## Comandos Uteis

```bash
# Subir apenas MLflow (+ dependencias)
docker compose up -d mlflow

# Ver logs do MLflow
docker compose logs -f mlflow

# Ver logs do Postgres do MLflow
docker compose logs -f mlflow_postgres

# Parar apenas MLflow
docker compose stop mlflow mlflow_postgres

# Remover e recriar
docker compose down mlflow mlflow_postgres
docker compose up -d mlflow

# Verificar status
docker compose ps mlflow mlflow_postgres
```

## Integracao com Outros Servicos do Core_SinapUm

Para logar experimentos a partir de outros servicos (ex: `openmind`, `sparkscore_service`), basta:

1. Adicionar `mlflow` ao `requirements.txt` do servico
2. Configurar a variavel `MLFLOW_TRACKING_URI=http://mlflow:5000` no environment do servico no `docker-compose.yml`
3. Usar a API do MLflow normalmente no codigo Python

## Nota Futura

- **Artifact Store em MinIO/S3**: Para producao, trocar o volume local por MinIO (S3-compatible) para artifacts distribuidos
- **Model Registry com staging**: Usar stages (Staging, Production) para gerenciar deploy de modelos
- **Autenticacao**: Adicionar autenticacao na UI com `--app-name basic-auth`
- **Integracao SparkScore/MotoPro**: Logar automaticamente modelos de IA dos servicos do Core_SinapUm
