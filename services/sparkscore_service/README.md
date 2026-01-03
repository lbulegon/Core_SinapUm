# SparkScore Service

## Sistema de Análise Psicológica e Semiótica

O SparkScore é um serviço de análise orbital de estímulos baseado na teoria de Peirce, fornecendo análise psicológica e semiótica completa.

### Descrição

Sistema de análise que combina:
- **Análise Psicológica**: Medição de atração, risco e ruído
- **Análise Semiótica**: Classificação baseada em teoria de Peirce (ícone, índice, símbolo)
- **Classificação Orbital**: 7 orbitais diferentes para classificação de estímulos
- **PPA (Ponto de Potencial de Atração)**: Análise de potencial de desenvolvimento

### Status do Serviço

- **Porta**: 8006
- **Framework**: FastAPI
- **Versão**: 1.0.0
- **Status**: ✅ Operacional

### Endpoints Disponíveis

#### 1. Health Check

**GET `/`**
- Descrição: Health check básico
- Resposta:
```json
{
  "service": "SparkScore - Sistema de Análise Psicológica e Semiótica",
  "status": "online",
  "version": "1.0.0"
}
```

**GET `/health`**
- Descrição: Health check detalhado
- Resposta:
```json
{
  "status": "healthy",
  "service": "SparkScore"
}
```

#### 2. Análise Completa

**POST `/sparkscore/analyze`**
- Descrição: Análise completa do estímulo (SparkScore + PPA + Orbital + Semiótica + Psicológica + Métricas)
- Body:
```json
{
  "stimulus": {
    "text": "texto do estímulo"
  },
  "context": {}
}
```
- Resposta: Retorna análise completa incluindo:
  - `sparkscore`: Score principal (0-1)
  - `ppa`: Status do PPA (inativo/ativo, stage, confidence, profile)
  - `orbital`: Classificação orbital (orbital dominante, orbitais secundários, grau de estabilidade)
  - `semiotic`: Análise semiótica (tipo Peirce, confidence, coerência)
  - `psycho`: Análise psicológica (atração, risco, ruído, intensidade emocional)
  - `metric`: Métricas (engajamento, conversão, qualidade)
  - `motor_result`: Resultado do motor de processamento
  - `recommendations`: Recomendações geradas

#### 3. Classificação Orbital

**POST `/sparkscore/classify-orbital`**
- Descrição: Classifica estímulo em orbital apenas
- Body:
```json
{
  "stimulus": {
    "text": "texto do estímulo"
  },
  "context": {}
}
```

#### 4. Análise Semiótica

**POST `/sparkscore/semiotic`**
- Descrição: Análise semiótica do estímulo
- Body:
```json
{
  "stimulus": {
    "text": "texto do estímulo"
  },
  "context": {}
}
```
- Resposta: Classifica tipo Peirce (icon, index, symbol) com confidence score

#### 5. Análise Psicológica

**POST `/sparkscore/psycho`**
- Descrição: Análise psicológica do estímulo
- Body:
```json
{
  "stimulus": {
    "text": "texto do estímulo"
  },
  "context": {}
}
```
- Resposta: Medição de atração, risco, ruído e intensidade emocional

#### 6. Análise Métrica

**POST `/sparkscore/metric`**
- Descrição: Análise métrica do estímulo
- Body:
```json
{
  "stimulus": {
    "text": "texto do estímulo"
  },
  "context": {}
}
```
- Resposta: Métricas de engajamento, conversão e qualidade

#### 7. Lista de Orbitais

**GET `/sparkscore/orbitals`**
- Descrição: Lista todos os orbitais disponíveis
- Resposta: Array com 7 orbitais (incluindo "Ruído", etc.)

#### 8. Documentação Interativa

**GET `/docs`**
- Descrição: Interface Swagger UI para documentação interativa
- Acesso: Navegador em `http://localhost:8006/docs`

**GET `/openapi.json`**
- Descrição: Especificação OpenAPI em JSON

### Exemplo de Uso

#### Análise Completa

```bash
curl -X POST http://localhost:8006/sparkscore/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "stimulus": {
      "text": "Exemplo de texto para análise"
    },
    "context": {}
  }'
```

#### Análise Semiótica

```bash
curl -X POST http://localhost:8006/sparkscore/semiotic \
  -H "Content-Type: application/json" \
  -d '{
    "stimulus": {
      "text": "Texto para análise semiótica"
    },
    "context": {}
  }'
```

#### Listar Orbitais

```bash
curl http://localhost:8006/sparkscore/orbitals
```

### Estrutura do Projeto

```
sparkscore_service/
├── app/
│   ├── agents/          # Agentes de análise
│   │   ├── semiotic_agent.py
│   │   ├── psycho_agent.py
│   │   └── metric_agent.py
│   ├── api/
│   │   └── routes.py    # Rotas da API
│   ├── core/
│   │   ├── sparkscore_calculator.py
│   │   └── orbital_classifier.py
│   ├── motors/          # Motores de processamento
│   ├── models/          # Modelos de dados
│   └── main.py          # Entrypoint FastAPI
├── config/              # Configurações
├── Dockerfile
├── docker-compose.yml
└── requirements.txt
```

### Execução

#### Via Docker Compose (Recomendado)

O serviço está integrado ao `docker-compose.yml` principal do Core_SinapUm:

```bash
cd /root/Core_SinapUm
docker compose up -d sparkscore_service
```

#### Standalone

```bash
cd services/sparkscore_service
docker compose up -d
```

### Verificação de Status

```bash
# Verificar logs
docker compose logs sparkscore_service

# Verificar status
docker compose ps sparkscore_service

# Testar health check
curl http://localhost:8006/health
```

### Notas Técnicas

- **Orbitais Disponíveis**: 7 orbitais diferentes para classificação
- **Teoria de Peirce**: Classificação em ícone, índice ou símbolo
- **PPA**: Ponto de Potencial de Atração com análise de stages
- **Motores**: Sistema de motores para processamento e filtragem

### Integração

O serviço está integrado à rede `mcp_network` do Core_SinapUm e pode ser acessado por outros serviços através do nome `sparkscore_service` na porta 8006.

### Observações

- O healthcheck do Docker pode mostrar como "unhealthy" devido à ausência de `curl` no container, mas o serviço funciona corretamente
- A documentação interativa está disponível em `/docs` (Swagger UI)
- Todos os endpoints retornam JSON

