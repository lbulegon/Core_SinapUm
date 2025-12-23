# MCP Service - Model Context Protocol Service

Serviço FastAPI que atua como gateway para tools versionadas seguindo o protocolo MCP (Model Context Protocol).

## 🎯 Objetivo

O MCP Service é o ponto de entrada para aplicações que precisam chamar tools versionadas. Ele:

- Consulta o **Core Registry** (Django) para resolver tools
- Desacopla aplicações de prompts diretos
- Permite versionamento de tools
- Executa runtimes (openmind_http, etc)
- Valida schemas de input/output
- Registra logs de auditoria

## 🚀 Como Subir

### Opção 1: Docker Compose (Recomendado)

```bash
cd /root/Core_SinapUm/services/mcp_service
docker compose up -d
```

### Opção 2: Via script principal

```bash
cd /root/Core_SinapUm
./restart_all_services.sh
```

## 🔧 Configuração

### Variáveis de Ambiente

- `SINAPUM_CORE_URL`: URL do Core Registry (Django)
  - Padrão: `http://69.169.102.84:5000`
  - Pode usar container_name se estiverem na mesma rede: `http://mcp_sinapum_web:5000`

- `OPENMIND_SERVICE_URL`: URL do OpenMind Service
  - Padrão: `http://69.169.102.84:8001`
  - Pode usar container_name: `http://openmind_service:8001`

### Porta

- **Porta fixa:** 7010
- **Base path:** `/mcp`

## 📋 Endpoints

### GET /health
Health check do MCP Service e status do Core Registry.

### GET /mcp/tools
Lista todas as tools disponíveis no registry.

### POST /mcp/call
Chama uma tool específica.

**Request:**
```json
{
  "tool": "vitrinezap.analisar_produto",
  "version": "1.0.0",
  "input": {
    "source": "image",
    "image_url": "http://example.com/image.jpg",
    "locale": "pt-BR",
    "mode": "fast"
  }
}
```

**Headers:**
```
X-SINAPUM-KEY: <api_key>
```

**Response:**
```json
{
  "request_id": "uuid",
  "tool": "vitrinezap.analisar_produto",
  "version": "1.0.0",
  "ok": true,
  "output": { ... },
  "latency_ms": 1234
}
```

## 🔄 Fluxo Completo

1. **Aplicação chama MCP Service:**
   ```
   POST http://localhost:7010/mcp/call
   Headers: X-SINAPUM-KEY: <api_key>
   ```

2. **MCP Service autentica e resolve tool:**
   ```
   POST http://69.169.102.84:5000/core/tools/resolve
   ```

3. **MCP Service valida input_schema**

4. **MCP Service executa runtime:**
   - Se `openmind_http`: POST no OpenMind Service
   - Outros runtimes: conforme implementado

5. **MCP Service valida output_schema**

6. **MCP Service registra log:**
   ```
   POST http://69.169.102.84:5000/core/tools/log
   ```

7. **MCP Service retorna resposta**

## 📦 Dependências

- `fastapi`: Framework web assíncrono
- `uvicorn`: Servidor ASGI
- `requests`: Cliente HTTP
- `pydantic`: Validação de dados
- `jsonschema`: Validação de JSON Schema

## 🐳 Docker

O MCP Service roda em seu próprio container Docker, seguindo o padrão dos outros serviços:

```bash
cd services/mcp_service
docker compose up -d
```

## ✅ Status

- ✅ MCP Service implementado
- ✅ Validação JSON Schema
- ✅ Runtime openmind_http
- ✅ Logging completo
- ✅ Integração com Core Registry
- ✅ Container Docker independente

