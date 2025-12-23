# Arquitetura de Serviços Independentes - MCP SinapUm

## 🎯 Princípio: Isolamento e Independência

Cada serviço no MCP SinapUm é **completamente independente**, garantindo que problemas em um serviço não afetem os outros.

## 📁 Estrutura de Diretórios

```
/root/MCP_SinapUm/services/
├── ddf_service/          # Porta 8005 - Detect & Delegate Framework
│   ├── docker-compose.yml
│   ├── Dockerfile
│   ├── requirements.txt
│   └── app/
│
├── sparkscore_service/   # Porta 8006 - Análise Psicológica e Semiótica
│   ├── docker-compose.yml
│   ├── Dockerfile
│   ├── requirements.txt
│   └── app/
│
├── evolution_api/        # Porta 8004 - WhatsApp Integration
│   ├── docker-compose.yml
│   └── (volumes: pg_data, redis_data, instances)
│
└── [outros serviços futuros]
```

## 🔒 Isolamento por Serviço

### 1. **Containers Docker Independentes**

Cada serviço tem seus próprios containers:
- **DDF**: `ddf_api`, `ddf_redis`, `ddf_postgres`
- **SparkScore**: `sparkscore_api`
- **Evolution API**: `evolution_api`, `postgres_evolution`, `redis_evolution`

### 2. **Portas Únicas**

Cada serviço usa portas dedicadas para evitar conflitos:
- **8004**: Evolution API
- **8005**: DDF API
- **8006**: SparkScore API
- **6380**: DDF Redis (evita conflito com Evolution Redis na 6379)
- **5434**: DDF PostgreSQL (evita conflito com outros PostgreSQL)

### 3. **Volumes e Dados Isolados**

Cada serviço gerencia seus próprios dados:
- **DDF**: `./storage`, `redis_data`, `postgres_data`
- **SparkScore**: (sem persistência por enquanto)
- **Evolution API**: `pg_data`, `redis_data`, `instances`

### 4. **Dependências Isoladas**

Cada serviço tem seu próprio `requirements.txt`:
- Dependências específicas por serviço
- Versões independentes
- Sem conflitos entre serviços

## ✅ Benefícios da Arquitetura

### 1. **Resiliência**
- Se o DDF cair, o SparkScore continua funcionando
- Se o Evolution API tiver problemas, os outros serviços não são afetados
- Falhas isoladas não causam cascata

### 2. **Manutenção Simplificada**
- Atualizar um serviço não afeta os outros
- Debugging isolado por serviço
- Deploy independente

### 3. **Escalabilidade**
- Escalar serviços individualmente
- Recursos dedicados por serviço
- Otimização independente

### 4. **Desenvolvimento Paralelo**
- Times podem trabalhar em serviços diferentes
- Testes isolados
- CI/CD independente

## 🔄 Comunicação Entre Serviços

Os serviços se comunicam via **HTTP REST APIs**:

```
┌─────────────┐      HTTP      ┌─────────────┐
│   DDF      │ ──────────────> │ SparkScore │
│  (8005)    │                 │   (8006)   │
└────────────┘                 └────────────┘
      │
      │ HTTP
      ▼
┌─────────────┐
│ Evolution  │
│   (8004)   │
└────────────┘
```

### Exemplo de Integração

```python
# DDF pode chamar SparkScore
import httpx

async def analyze_with_sparkscore(stimulus: str):
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "http://sparkscore_api:8006/sparkscore/analyze",
            json={"stimulus": stimulus}
        )
        return response.json()
```

## 🛠️ Gerenciamento de Serviços

### Subir um serviço específico

```bash
cd /root/MCP_SinapUm/services/ddf_service
docker compose up -d
```

### Parar um serviço específico

```bash
cd /root/MCP_SinapUm/services/ddf_service
docker compose down
```

### Verificar status de todos os serviços

```bash
docker ps | grep -E "ddf|sparkscore|evolution"
```

## 📊 Monitoramento Independente

Cada serviço expõe seus próprios endpoints de health:

- **DDF**: `http://localhost:8005/health`
- **SparkScore**: `http://localhost:8006/health`
- **Evolution API**: `http://localhost:8004`

## 🔐 Segurança

- Cada serviço pode ter suas próprias políticas de segurança
- Tokens e credenciais isolados
- Firewall e acesso controlado por serviço

## 🚀 Próximos Serviços

A arquitetura permite adicionar novos serviços facilmente:

```
services/
├── ddf_service/          ✅
├── sparkscore_service/   ✅
├── evolution_api/        ✅
├── kmn_service/          🔜 (Porta 8007)
└── [outros serviços]     🔜
```

Cada novo serviço seguirá o mesmo padrão de isolamento.

## 📝 Checklist para Novos Serviços

Ao adicionar um novo serviço, garantir:

- [ ] Diretório próprio em `/root/MCP_SinapUm/services/`
- [ ] `docker-compose.yml` próprio
- [ ] `Dockerfile` próprio
- [ ] `requirements.txt` próprio
- [ ] Porta única e não conflitante
- [ ] Volumes e dados isolados
- [ ] Endpoint `/health` para monitoramento
- [ ] Documentação no `README.md` do serviço

---

**Conclusão**: Esta arquitetura garante que cada serviço seja uma unidade independente, facilitando manutenção, escalabilidade e resiliência do sistema como um todo.

