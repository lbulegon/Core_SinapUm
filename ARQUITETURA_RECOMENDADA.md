# 🏗️ Arquitetura Recomendada para MCP_SinapUm

**Data:** 2025-01-13  
**Versão:** 1.0.0  
**Status:** Recomendação de Arquitetura

---

## 📋 Visão Geral

Este documento descreve a **arquitetura recomendada** para o projeto MCP_SinapUm, combinando Django, FastAPI, Evolution API e **Model Context Protocol (MCP)** de forma otimizada para atender às necessidades do projeto.

**Componentes principais:**
- **Django** - Orquestrador principal e sistema administrativo
- **FastAPI** - Serviços especializados de alta performance
- **Evolution API** - Integração com WhatsApp
- **Model Context Protocol (MCP)** - Protocolo oficial para integração com Claude Desktop e outros LLMs

---

## 🎯 Princípios da Arquitetura

### 1. **Django como Orquestrador Principal**
- ✅ Admin, Models, ORM
- ✅ Master Control Program (interno)
- ✅ Sistema completo e maduro
- ✅ Reutilização de código existente

### 2. **FastAPI para Serviços Especializados**
- ✅ Alta performance
- ✅ Assíncrono nativo
- ✅ APIs modernas
- ✅ Serviços independentes e escaláveis

### 3. **Integração via HTTP**
- ✅ Comunicação entre serviços via HTTP
- ✅ Cada serviço é independente
- ✅ Fácil de escalar e manter
- ✅ Fácil de testar

### 4. **Evolution API para WhatsApp**
- ✅ Integração com WhatsApp via Evolution API
- ✅ Gerenciamento de instâncias WhatsApp
- ✅ Envio e recebimento de mensagens
- ✅ Webhooks e eventos

### 5. **Model Context Protocol (MCP) Oficial**
- ✅ Protocolo oficial da Anthropic para conectar LLMs a ferramentas
- ✅ Integração com Claude Desktop
- ✅ Exposição de tools, resources e prompts
- ✅ Padrão aberto e padronizado

---

## 🏗️ Arquitetura Recomendada

### Mapeamento Rápido de Portas

| Porta | Serviço | Status | Framework |
|-------|---------|--------|-----------|
| **5000** | SinapUm Django | ✅ Ativo | Django |
| **8000** | OpenMind AI Server | ✅ Ativo | FastAPI |
| **8001** | Product Service | 🆕 Recomendado | FastAPI |
| **8002** | CrewAI Service | 🆕 Recomendado | FastAPI |
| **8003** | Agnos Service | 🆕 Recomendado | FastAPI |
| **8004** | Evolution API | ✅ Ativo | Docker |
| **8005** | MotoPro Service | 🔮 Futuro | FastAPI |
| **8006** | SparkScore Service | 🔮 Futuro | FastAPI |
| **8007** | KMN Service | 🔮 Futuro | FastAPI |
| **MCP** | MCP Server SinapUm | 🆕 Recomendado | Python (stdio/HTTP) |
| **5432** | SinapUm PostgreSQL | ✅ Ativo | PostgreSQL |
| **5433** | Evolution PostgreSQL | ✅ Ativo | PostgreSQL |
| **6379** | Evolution Redis | ✅ Ativo | Redis |

### Diagrama de Arquitetura

```
┌─────────────────────────────────────────────────────────────┐
│                    Clientes Externos                         │
│  (VitrineZap, MotoPro, Eventix, SparkScore, etc.)           │
└───────────────────────┬─────────────────────────────────────┘
                        │ HTTP/HTTPS
                        ▼
┌─────────────────────────────────────────────────────────────┐
│              SinapUm Django (Porta 5000)                     │
│  ┌───────────────────────────────────────────────────────┐ │
│  │  Orquestrador Principal                                 │ │
│  │  - Master Control Program (interno)                    │ │
│  │  - MCP Router                                           │ │
│  │  - Agent Registry                                       │ │
│  │  - Telemetria                                           │ │
│  └───────────────────────────────────────────────────────┘ │
│  ┌───────────────────────────────────────────────────────┐ │
│  │  Sistema Django Completo                                │ │
│  │  - Admin Django                                         │ │
│  │  - Models (ORM)                                         │ │
│  │  - Views                                                │ │
│  │  - Migrations                                           │ │
│  │  - Templates (se necessário)                            │ │
│  └───────────────────────────────────────────────────────┘ │
└───┬─────────────────────────────────────────────────────────┘
    │ HTTP Requests (requests/httpx)
    │
    ├───→ ┌─────────────────────────────────────────────┐
    │     │  OpenMind AI Server (FastAPI - Porta 8000)  │
    │     │  ✅ Já implementado                         │
    │     │  - Análise de imagens                       │
    │     │  - Extração de dados                        │
    │     │  - Processamento de IA                      │
    │     └─────────────────────────────────────────────┘
    │
    ├───→ ┌─────────────────────────────────────────────┐
    │     │  Product Service (FastAPI - Porta 8001)     │
    │     │  🆕 Recomendado para implementar            │
    │     │  - Gerenciamento de produtos                │
    │     │  - Catálogo                                 │
    │     │  - Validação de produtos                    │
    │     └─────────────────────────────────────────────┘
    │
    ├───→ ┌─────────────────────────────────────────────┐
    │     │  CrewAI Service (FastAPI - Porta 8002)     │
    │     │  🆕 Recomendado para implementar            │
    │     │  - Orquestração de agentes                 │
    │     │  - Análise complexa                        │
    │     │  - Workflows multi-agente                  │
    │     └─────────────────────────────────────────────┘
    │
    ├───→ ┌─────────────────────────────────────────────┐
    │     │  Agnos Service (FastAPI - Porta 8003)      │
    │     │  🆕 Recomendado para implementar            │
    │     │  - Workflows de alto nível                 │
    │     │  - Validação de dados                      │
    │     │  - Processamento em pipeline               │
    │     └─────────────────────────────────────────────┘
    │
    ├───→ ┌─────────────────────────────────────────────┐
    │     │  Evolution API (Porta 8004)                  │
    │     │  ✅ Já implementado                         │
    │     │  - Integração WhatsApp                      │
    │     │  - Gerenciamento de instâncias              │
    │     │  - Envio/recebimento de mensagens           │
    │     │  - Webhooks                                 │
    │     │  - PostgreSQL (5433)                        │
    │     │  - Redis (cache)                            │
    │     └─────────────────────────────────────────────┘
    │
    └───→ ┌─────────────────────────────────────────────┐
          │  Outros Serviços Futuros                    │
          │  - MotoPro Service (8005)                   │
          │  - SparkScore Service (8006)                │
          │  - KMN Service (8007)                       │
          └─────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│              Model Context Protocol (MCP)                    │
│  ┌───────────────────────────────────────────────────────┐ │
│  │  MCP Server SinapUm (stdio/HTTP)                      │ │
│  │  🆕 Recomendado para implementar                      │ │
│  │  - Tools: analyze_product_image                       │ │
│  │  - Tools: send_whatsapp_message                       │ │
│  │  - Tools: list_products, get_product                 │ │
│  │  - Tools: analyze_with_crewai                        │ │
│  │  - Resources: products, whatsapp_instances          │ │
│  │  - Prompts: product_analysis, whatsapp_message       │ │
│  └───────────────────────────────────────────────────────┘ │
└───┬─────────────────────────────────────────────────────────┘
    │ MCP Protocol (JSON-RPC)
    │
    └───→ ┌─────────────────────────────────────────────┐
          │  Claude Desktop / Outros Clientes MCP       │
          │  - Interface para LLMs                       │
          │  - Acesso a ferramentas do SinapUm           │
          │  - Integração oficial Anthropic              │
          └─────────────────────────────────────────────┘
```

---

## 🔄 Fluxo de Requisição

### Exemplo 1: Análise de Imagem de Produto

```
1. Cliente (VitrineZap)
   ↓ POST /api/v1/analyze-product-image
   
2. SinapUm Django (Porta 5000)
   ├─> Recebe requisição
   ├─> Valida dados
   ├─> Salva imagem (se necessário)
   ├─> Master Control Program roteia tarefa
   └─> Agent OpenMind é selecionado
       ↓
   
3. Agent OpenMind (Django)
   ├─> Prepara dados
   └─> Chama serviço FastAPI
       ↓ HTTP POST
       
4. OpenMind AI Server (FastAPI - Porta 8000)
   ├─> Recebe requisição
   ├─> Processa imagem (assíncrono)
   ├─> Chama API OpenMind.org
   ├─> Extrai dados estruturados
   └─> Retorna JSON
       ↓ HTTP Response
       
5. Agent OpenMind (Django)
   ├─> Recebe resposta
   ├─> Processa resultado
   └─> Retorna para MCP Router
       ↓
       
6. SinapUm Django
   ├─> Formata resposta
   ├─> Adiciona telemetria
   └─> Retorna para cliente
       ↓
       
7. Cliente (VitrineZap)
   └─> Recebe resposta completa
```

### Exemplo 2: Envio de Mensagem WhatsApp com Produto

```
1. Cliente (VitrineZap)
   ↓ POST /api/v1/send-product-whatsapp
   { "phone": "+5511999999999", "product_id": 123 }
   
2. SinapUm Django (Porta 5000)
   ├─> Recebe requisição
   ├─> Busca produto no banco (ORM Django)
   ├─> Master Control Program roteia tarefa
   └─> Agent VitrineZap é selecionado
       ↓
   
3. Agent VitrineZap (Django)
   ├─> Prepara mensagem com dados do produto
   ├─> Formata mensagem para WhatsApp
   └─> Chama Evolution API
       ↓ HTTP POST
       
4. Evolution API (Porta 8004)
   ├─> Recebe requisição
   ├─> Valida instância WhatsApp
   ├─> Envia mensagem via WhatsApp
   └─> Retorna status
       ↓ HTTP Response
       
5. Agent VitrineZap (Django)
   ├─> Recebe resposta
   ├─> Registra envio no banco
   └─> Retorna para MCP Router
       ↓
       
6. SinapUm Django
   ├─> Formata resposta
   ├─> Adiciona telemetria
   └─> Retorna para cliente
       ↓
       
7. Cliente (VitrineZap)
   └─> Recebe confirmação de envio
```

### Exemplo 3: Recebimento de Mensagem WhatsApp

```
1. WhatsApp → Evolution API (Porta 8004)
   ↓ Webhook (mensagem recebida)
   
2. Evolution API
   ├─> Processa mensagem
   ├─> Salva no PostgreSQL
   └─> Envia webhook para Django
       ↓ HTTP POST
       
3. SinapUm Django (Porta 5000)
   ├─> Recebe webhook em /api/webhooks/evolution/
   ├─> Processa mensagem recebida
   ├─> Extrai dados (texto, mídia, etc.)
   └─> Master Control Program roteia tarefa
       ↓
       
4. Agent apropriado (ex: Agent VitrineZap)
   ├─> Analisa mensagem
   ├─> Processa comando (ex: "buscar produto X")
   ├─> Busca dados necessários
   └─> Prepara resposta
       ↓
       
5. Agent chama Evolution API
   ├─> Envia resposta via WhatsApp
   └─> Retorna status
       ↓
       
6. Evolution API → WhatsApp
   └─> Mensagem entregue ao usuário
```

---

## 📦 Componentes da Arquitetura

### 1. SinapUm Django (Orquestrador Principal)

**Localização:** `/root/MCP_SinapUm/`  
**Porta:** `5000`  
**Framework:** Django 4.2+

**Responsabilidades:**
- ✅ Orquestração central (Master Control Program)
- ✅ Roteamento de tarefas
- ✅ Gerenciamento de agentes
- ✅ Admin e interface administrativa
- ✅ Models e ORM (banco de dados)
- ✅ Telemetria e logs
- ✅ Autenticação e autorização

**Estrutura:**
```
MCP_SinapUm/
├── app_sinapum/
│   ├── mcp/                    # Master Control Program
│   │   ├── core/
│   │   │   ├── router.py      # MCP Router
│   │   │   ├── registry.py    # Agent Registry
│   │   │   └── telemetry.py   # Telemetria
│   │   ├── agents/
│   │   │   ├── agent_openmind.py
│   │   │   ├── agent_vitrinezap.py
│   │   │   ├── agent_crewai.py
│   │   │   └── agent_agnos.py
│   │   └── schemas/
│   ├── views.py                # Views Django
│   ├── models.py               # Models Django
│   ├── services.py             # Serviços (chama FastAPI)
│   └── admin.py                # Admin Django
├── setup/
│   ├── settings.py
│   └── urls.py
└── manage.py
```

**Endpoints principais:**
- `/mcp/route-task` - Endpoint principal do MCP
- `/mcp/agents` - Listar agentes disponíveis
- `/api/v1/analyze-product-image` - API REST (compatibilidade)
- `/admin/` - Admin Django

---

### 2. OpenMind AI Server (FastAPI)

**Localização:** `/opt/openmind-ai/`  
**Porta:** `8000`  
**Framework:** FastAPI  
**Status:** ✅ Já implementado

**Responsabilidades:**
- ✅ Análise de imagens de produtos
- ✅ Extração de dados via IA
- ✅ Geração de JSON estruturado
- ✅ Processamento assíncrono de alta performance

**Endpoints:**
- `POST /api/v1/analyze-product-image` - Análise de imagem
- `GET /health` - Health check
- `GET /docs` - Documentação Swagger

**Integração:**
```python
# Django chama FastAPI
response = requests.post(
    "http://127.0.0.1:8000/api/v1/analyze-product-image",
    files={'image': image_file}
)
```

---

### 3. Product Service (FastAPI) - Recomendado

**Localização:** `/root/MCP_SinapUm/services/product_service/`  
**Porta:** `8001`  
**Framework:** FastAPI  
**Status:** 🆕 Recomendado para implementar

**Responsabilidades:**
- ✅ Gerenciamento de produtos
- ✅ Catálogo de produtos
- ✅ Validação de produtos
- ✅ Busca e filtros
- ✅ APIs públicas de alta performance

**Endpoints sugeridos:**
- `GET /api/products/` - Listar produtos
- `GET /api/products/{id}` - Obter produto
- `POST /api/products/` - Criar produto
- `PUT /api/products/{id}` - Atualizar produto
- `DELETE /api/products/{id}` - Deletar produto
- `GET /api/products/search?q=...` - Buscar produtos

**Integração:**
```python
# Django chama FastAPI
async with httpx.AsyncClient() as client:
    response = await client.get("http://127.0.0.1:8001/api/products/")
    return response.json()
```

**Django expõe endpoint interno:**
```python
# app_sinapum/views.py
@csrf_exempt
def api_internal_list_products(request):
    """Endpoint interno para FastAPI chamar"""
    products = Product.objects.all()  # ORM Django
    return JsonResponse({'products': [...]})
```

---

### 4. CrewAI Service (FastAPI) - Recomendado

**Localização:** `/root/MCP_SinapUm/services/crewai_service/`  
**Porta:** `8002`  
**Framework:** FastAPI  
**Status:** 🆕 Recomendado para implementar

**Responsabilidades:**
- ✅ Orquestração de múltiplos agentes
- ✅ Análise complexa com múltiplas LLMs
- ✅ Workflows de análise avançada
- ✅ Processamento assíncrono

**Endpoints sugeridos:**
- `POST /api/crewai/analyze` - Análise com CrewAI
- `POST /api/crewai/orchestrate` - Orquestrar análise completa
- `GET /api/crewai/status/{task_id}` - Status da tarefa

**Integração:**
```python
# Django chama FastAPI
async with httpx.AsyncClient() as client:
    response = await client.post(
        "http://127.0.0.1:8002/api/crewai/analyze",
        json={"image_url": "...", "context": "..."}
    )
    return response.json()
```

---

### 5. Evolution API (WhatsApp Integration)

**Localização:** `/root/evolution_api/`  
**Porta:** `8004` (HTTP), `5433` (PostgreSQL), `6379` (Redis)  
**Framework:** Docker Container (atendai/evolution-api)  
**Status:** ✅ Já implementado

**Responsabilidades:**
- ✅ Integração com WhatsApp
- ✅ Gerenciamento de instâncias WhatsApp
- ✅ Envio e recebimento de mensagens
- ✅ Webhooks e eventos
- ✅ Persistência de mensagens e contatos
- ✅ Cache com Redis

**Componentes:**
- **Evolution API Container** - API principal (porta 8004)
- **PostgreSQL** - Banco de dados (porta 5433)
- **Redis** - Cache e sessões (porta 6379)

**Endpoints principais:**
- `POST /instance/create` - Criar instância WhatsApp
- `POST /instance/connect/{instance}` - Conectar instância
- `POST /message/sendText/{instance}` - Enviar mensagem de texto
- `POST /message/sendMedia/{instance}` - Enviar mídia
- `GET /message/fetchMessages/{instance}` - Buscar mensagens
- `POST /webhook/set/{instance}` - Configurar webhook
- `GET /instance/fetchInstances` - Listar instâncias

**Configuração:**
```yaml
# docker-compose.yml
services:
  evolution_api:
    image: atendai/evolution-api:v2.1.1
    ports:
      - "8004:8080"
    environment:
      - SERVER_URL=http://69.169.102.84:8004
      - AUTHENTICATION_API_KEY=GKvy6psn-8HHpBQ4HAHKFOXnwjHR-oSzeGZzCaws0xg
      - DATABASE_ENABLED=true
      - DATABASE_PROVIDER=postgresql
      - CACHE_REDIS_ENABLED=true
```

**Integração com Django:**
```python
# app_sinapum/services.py
import requests
from django.conf import settings

EVOLUTION_API_URL = getattr(settings, 'EVOLUTION_API_URL', 'http://127.0.0.1:8004')
EVOLUTION_API_KEY = getattr(settings, 'EVOLUTION_API_KEY', 'GKvy6psn-8HHpBQ4HAHKFOXnwjHR-oSzeGZzCaws0xg')

def send_whatsapp_message(instance_name, phone, message):
    """Enviar mensagem via WhatsApp usando Evolution API"""
    url = f"{EVOLUTION_API_URL}/message/sendText/{instance_name}"
    
    headers = {
        'apikey': EVOLUTION_API_KEY,
        'Content-Type': 'application/json'
    }
    
    payload = {
        "number": phone,
        "text": message
    }
    
    response = requests.post(url, json=payload, headers=headers)
    return response.json()

def send_whatsapp_media(instance_name, phone, media_url, caption=None):
    """Enviar mídia via WhatsApp"""
    url = f"{EVOLUTION_API_URL}/message/sendMedia/{instance_name}"
    
    headers = {
        'apikey': EVOLUTION_API_KEY,
        'Content-Type': 'application/json'
    }
    
    payload = {
        "number": phone,
        "mediaUrl": media_url,
        "caption": caption or ""
    }
    
    response = requests.post(url, json=payload, headers=headers)
    return response.json()
```

**Webhook para receber mensagens:**
```python
# app_sinapum/views.py
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json

@csrf_exempt
def evolution_webhook(request):
    """Receber webhooks do Evolution API"""
    if request.method == 'POST':
        data = json.loads(request.body)
        
        # Processar evento
        event_type = data.get('event')
        
        if event_type == 'messages.upsert':
            # Nova mensagem recebida
            message = data.get('data', {})
            from_number = message.get('key', {}).get('remoteJid', '')
            message_text = message.get('message', {}).get('conversation', '')
            
            # Processar mensagem (ex: análise de produto)
            # ...
            
        elif event_type == 'messages.update':
            # Mensagem atualizada (status de entrega, leitura, etc.)
            # ...
        
        return JsonResponse({'status': 'ok'})
    
    return JsonResponse({'error': 'Method not allowed'}, status=405)
```

**Configuração no Django:**
```python
# setup/settings.py
EVOLUTION_API_URL = 'http://127.0.0.1:8004'
EVOLUTION_API_KEY = 'GKvy6psn-8HHpBQ4HAHKFOXnwjHR-oSzeGZzCaws0xg'
EVOLUTION_WEBHOOK_URL = 'http://69.169.102.84:5000/api/webhooks/evolution/'
```

**URLs:**
```python
# setup/urls.py
urlpatterns = [
    # ... outras rotas
    path('api/webhooks/evolution/', views.evolution_webhook, name='evolution_webhook'),
]
```

---

### 6. Model Context Protocol Server (MCP) - Recomendado

**Localização:** `/root/MCP_SinapUm/mcp_server_sinapum/`  
**Protocolo:** MCP (JSON-RPC sobre stdio/HTTP)  
**Framework:** Python (biblioteca `mcp`)  
**Status:** 🆕 Recomendado para implementar

**Responsabilidades:**
- ✅ Expor ferramentas do SinapUm para Claude Desktop
- ✅ Conectar LLMs aos serviços existentes
- ✅ Padrão oficial da Anthropic
- ✅ Integração com Claude Desktop e outros clientes MCP

**Estrutura:**
```
mcp_server_sinapum/
├── __init__.py
├── server.py              # Servidor MCP principal
├── tools/
│   ├── __init__.py
│   ├── image_analysis.py  # Tool: analyze_product_image
│   ├── whatsapp.py        # Tool: send_whatsapp_message
│   ├── products.py        # Tool: list_products, get_product
│   └── crewai.py          # Tool: analyze_with_crewai
├── resources/
│   ├── __init__.py
│   ├── products.py        # Resource: produtos do catálogo
│   └── instances.py        # Resource: instâncias WhatsApp
└── prompts/
    ├── __init__.py
    └── analysis.py        # Prompts: templates de análise
```

**Tools (Ferramentas) expostas:**
- `analyze_product_image` - Analisa imagem de produto usando OpenMind AI
- `send_whatsapp_message` - Envia mensagem via WhatsApp usando Evolution API
- `list_products` - Lista produtos do catálogo
- `get_product` - Obtém detalhes de um produto
- `analyze_with_crewai` - Análise complexa usando CrewAI
- `validate_with_agnos` - Validação de dados usando Agnos

**Resources (Recursos) expostos:**
- `products` - Catálogo de produtos
- `whatsapp_instances` - Instâncias WhatsApp configuradas
- `analysis_history` - Histórico de análises

**Prompts (Templates):**
- `product_analysis` - Template para análise de produtos
- `whatsapp_message` - Template para mensagens WhatsApp

**Implementação:**
```python
# mcp_server_sinapum/server.py
from mcp.server import Server
from mcp.types import Tool, Resource, Prompt
import httpx

server = Server("sinapum-mcp")

@server.list_tools()
async def list_tools() -> list[Tool]:
    """Lista todas as tools disponíveis"""
    return [
        Tool(
            name="analyze_product_image",
            description="Analisa imagem de produto usando OpenMind AI",
            inputSchema={
                "type": "object",
                "properties": {
                    "image_url": {
                        "type": "string",
                        "description": "URL da imagem do produto"
                    },
                    "language": {
                        "type": "string",
                        "default": "pt-BR",
                        "description": "Idioma da análise"
                    }
                },
                "required": ["image_url"]
            }
        ),
        Tool(
            name="send_whatsapp_message",
            description="Envia mensagem via WhatsApp usando Evolution API",
            inputSchema={
                "type": "object",
                "properties": {
                    "instance": {
                        "type": "string",
                        "description": "Nome da instância WhatsApp"
                    },
                    "phone": {
                        "type": "string",
                        "description": "Número do telefone (formato: 5511999999999)"
                    },
                    "message": {
                        "type": "string",
                        "description": "Texto da mensagem"
                    }
                },
                "required": ["instance", "phone", "message"]
            }
        ),
        Tool(
            name="list_products",
            description="Lista produtos do catálogo",
            inputSchema={
                "type": "object",
                "properties": {
                    "limit": {
                        "type": "integer",
                        "default": 10,
                        "description": "Número máximo de produtos"
                    },
                    "search": {
                        "type": "string",
                        "description": "Termo de busca"
                    }
                }
            }
        )
    ]

@server.call_tool()
async def call_tool(name: str, arguments: dict) -> dict:
    """Executa uma tool"""
    if name == "analyze_product_image":
        # Chama Django/OpenMind AI
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "http://127.0.0.1:5000/api/v1/analyze-product-image",
                files={"image": arguments["image_url"]}
            )
            return {"result": response.json()}
    
    elif name == "send_whatsapp_message":
        # Chama Evolution API via Django
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "http://127.0.0.1:5000/api/internal/send-whatsapp",
                json={
                    "instance": arguments["instance"],
                    "phone": arguments["phone"],
                    "message": arguments["message"]
                }
            )
            return {"result": response.json()}
    
    elif name == "list_products":
        # Chama Django
        async with httpx.AsyncClient() as client:
            response = await client.get(
                "http://127.0.0.1:5000/api/internal/products/",
                params={"limit": arguments.get("limit", 10)}
            )
            return {"result": response.json()}
    
    else:
        raise ValueError(f"Tool {name} não encontrada")

@server.list_resources()
async def list_resources() -> list[Resource]:
    """Lista recursos disponíveis"""
    return [
        Resource(
            uri="products://catalog",
            name="Catálogo de Produtos",
            description="Acesso ao catálogo completo de produtos",
            mimeType="application/json"
        ),
        Resource(
            uri="whatsapp://instances",
            name="Instâncias WhatsApp",
            description="Lista de instâncias WhatsApp configuradas",
            mimeType="application/json"
        )
    ]

@server.read_resource()
async def read_resource(uri: str) -> str:
    """Lê um recurso"""
    if uri == "products://catalog":
        async with httpx.AsyncClient() as client:
            response = await client.get("http://127.0.0.1:5000/api/internal/products/")
            return response.text
    elif uri == "whatsapp://instances":
        async with httpx.AsyncClient() as client:
            response = await client.get("http://127.0.0.1:8004/instance/fetchInstances")
            return response.text
    else:
        raise ValueError(f"Resource {uri} não encontrado")

async def main():
    """Executa o servidor MCP"""
    async with server:
        await server.run()

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
```

**Configuração para Claude Desktop:**
```json
{
  "mcpServers": {
    "sinapum": {
      "command": "python",
      "args": ["-m", "mcp_server_sinapum"],
      "env": {
        "DJANGO_SETTINGS_MODULE": "setup.settings",
        "OPENMIND_AI_URL": "http://127.0.0.1:8000",
        "EVOLUTION_API_URL": "http://127.0.0.1:8004"
      }
    }
  }
}
```

**Localização do arquivo de configuração:**
- **Linux:** `~/.config/claude_desktop_config.json`
- **Windows:** `%APPDATA%\Claude\claude_desktop_config.json`
- **macOS:** `~/Library/Application Support/Claude/claude_desktop_config.json`

**Integração com serviços existentes:**
```
Claude Desktop
    ↓ MCP Protocol (JSON-RPC)
MCP Server SinapUm
    ↓ HTTP Requests
SinapUm Django (5000)
    ├──→ OpenMind AI (8000)
    ├──→ Evolution API (8004)
    └──→ Outros serviços
```

**Fluxo de exemplo:**
```
1. Claude Desktop solicita análise de imagem
   ↓ MCP call_tool("analyze_product_image", {...})
   
2. MCP Server SinapUm
   ├─> Recebe requisição via MCP
   ├─> Valida argumentos
   └─> Chama Django via HTTP
       ↓
       
3. SinapUm Django
   ├─> Recebe requisição
   ├─> Processa via OpenMind AI
   └─> Retorna resultado
       ↓
       
4. MCP Server SinapUm
   ├─> Recebe resposta
   └─> Retorna via MCP
       ↓
       
5. Claude Desktop
   └─> Exibe resultado para o usuário
```

**Vantagens:**
- ✅ Integração oficial com Claude Desktop
- ✅ Padrão aberto e padronizado
- ✅ Reutiliza todos os serviços existentes
- ✅ Não quebra código existente
- ✅ Expõe ferramentas de forma padronizada

---

### 7. Agnos Service (FastAPI) - Recomendado

**Localização:** `/root/MCP_SinapUm/services/agnos_service/`  
**Porta:** `8003`  
**Framework:** FastAPI  
**Status:** 🆕 Recomendado para implementar

**Responsabilidades:**
- ✅ Workflows de alto nível
- ✅ Validação de dados
- ✅ Processamento em pipeline
- ✅ Regras de negócio complexas

**Endpoints sugeridos:**
- `POST /api/agnos/validate` - Validar dados
- `POST /api/agnos/workflow` - Executar workflow
- `GET /api/agnos/workflows` - Listar workflows

**Integração:**
```python
# Django chama FastAPI
async with httpx.AsyncClient() as client:
    response = await client.post(
        "http://127.0.0.1:8003/api/agnos/validate",
        json={"data": {...}}
    )
    return response.json()
```

---

## 🔌 Comunicação Entre Serviços

### Padrão de Comunicação

**Django → FastAPI:**
```python
# Síncrono (requests)
import requests

response = requests.post(
    "http://127.0.0.1:8000/api/v1/analyze-product-image",
    files={'image': image_file},
    timeout=60
)
result = response.json()

# Assíncrono (httpx) - Recomendado
import httpx

async with httpx.AsyncClient() as client:
    response = await client.post(
        "http://127.0.0.1:8000/api/v1/analyze-product-image",
        files={'image': image_file}
    )
    result = response.json()
```

**FastAPI → Django:**
```python
# FastAPI chama Django (endpoints internos)
async with httpx.AsyncClient() as client:
    response = await client.get(
        "http://127.0.0.1:5000/api/internal/products/"
    )
    products = response.json()
```

---

## 📊 Portas e Configuração

### Mapeamento Completo de Serviços

#### Serviços Principais

| Serviço | Porta | Protocolo | Localização | Status | Framework |
|---------|-------|-----------|-------------|--------|-----------|
| **SinapUm Django** | 5000 | HTTP | `/root/MCP_SinapUm/` | ✅ Ativo | Django 4.2+ |
| **OpenMind AI Server** | 8000 | HTTP | `/opt/openmind-ai/` | ✅ Ativo | FastAPI |
| **Product Service** | 8001 | HTTP | `/root/MCP_SinapUm/services/product_service/` | 🆕 Recomendado | FastAPI |
| **CrewAI Service** | 8002 | HTTP | `/root/MCP_SinapUm/services/crewai_service/` | 🆕 Recomendado | FastAPI |
| **Agnos Service** | 8003 | HTTP | `/root/MCP_SinapUm/services/agnos_service/` | 🆕 Recomendado | FastAPI |
| **Evolution API** | 8004 | HTTP | `/root/evolution_api/` | ✅ Ativo | Docker Container |

#### Bancos de Dados e Cache

| Serviço | Porta | Protocolo | Localização | Status | Tipo |
|---------|-------|-----------|-------------|--------|------|
| **Evolution PostgreSQL** | 5433 | TCP | `/root/evolution_api/` | ✅ Ativo | PostgreSQL 16 |
| **Evolution Redis** | 6379 | TCP | `/root/evolution_api/` | ✅ Ativo | Redis 7 |
| **SinapUm Database** | 5432 | TCP | Docker/PostgreSQL | ✅ Ativo | PostgreSQL |

#### Serviços Futuros

| Serviço | Porta | Protocolo | Localização | Status | Framework |
|---------|-------|-----------|-------------|--------|-----------|
| **MotoPro Service** | 8005 | HTTP | `/root/MCP_SinapUm/services/motopro_service/` | 🔮 Futuro | FastAPI |
| **SparkScore Service** | 8006 | HTTP | `/root/MCP_SinapUm/services/sparkscore_service/` | 🔮 Futuro | FastAPI |
| **KMN Service** | 8007 | HTTP | `/root/MCP_SinapUm/services/kmn_service/` | 🔮 Futuro | FastAPI |

### Resumo por Categoria

#### ✅ Serviços Ativos (Produção)

```
┌─────────────────────────────────────────────────────────┐
│  SinapUm Django (5000)                                   │
│  ├─> Orquestrador Principal                              │
│  ├─> Master Control Program                              │
│  ├─> Admin Django                                        │
│  └─> ORM e Models                                        │
└─────────────────────────────────────────────────────────┘
         │
         ├──→ OpenMind AI (8000) - Análise de imagens
         └──→ Evolution API (8004) - WhatsApp
                ├──→ PostgreSQL (5433)
                └──→ Redis (6379)
```

#### 🆕 Serviços Recomendados (A Implementar)

```
┌─────────────────────────────────────────────────────────┐
│  Product Service (8001)                                 │
│  ├─> Gerenciamento de produtos                         │
│  ├─> Catálogo                                           │
│  └─> Validação                                          │
└─────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────┐
│  CrewAI Service (8002)                                  │
│  ├─> Orquestração de agentes                           │
│  ├─> Análise complexa                                   │
│  └─> Workflows multi-agente                             │
└─────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────┐
│  Agnos Service (8003)                                   │
│  ├─> Workflows de alto nível                           │
│  ├─> Validação de dados                                │
│  └─> Processamento em pipeline                         │
└─────────────────────────────────────────────────────────┘
```

#### 🔮 Serviços Futuros (Planejados)

```
┌─────────────────────────────────────────────────────────┐
│  MotoPro Service (8005)                                 │
│  ├─> Distribuição de vagas                              │
│  ├─> Gestão de turnos                                   │
│  └─> Raio 300m                                          │
└─────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────┐
│  SparkScore Service (8006)                              │
│  ├─> Análise psicológica                                │
│  ├─> PPA automático                                     │
│  └─> Pontuação de ofertas                              │
└─────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────┐
│  KMN Service (8007)                                     │
│  ├─> Keeper Mesh Network                                │
│  ├─> Decisão de entrega                                │
│  └─> Resolução de conflitos                            │
└─────────────────────────────────────────────────────────┘
```

### Sequência de Portas (Padronização)

```
Porta 5000: SinapUm Django (Orquestrador Principal)
Porta 8000: OpenMind AI Server (Análise de Imagens)
Porta 8001: Product Service (Produtos)
Porta 8002: CrewAI Service (Agentes)
Porta 8003: Agnos Service (Workflows)
Porta 8004: Evolution API (WhatsApp)
Porta 8005: MotoPro Service (Futuro)
Porta 8006: SparkScore Service (Futuro)
Porta 8007: KMN Service (Futuro)
```

### Portas de Banco de Dados e Cache

```
Porta 5432: SinapUm PostgreSQL (Banco principal Django)
Porta 5433: Evolution PostgreSQL (Banco Evolution API)
Porta 6379: Evolution Redis (Cache Evolution API)
```

### Configuração de URLs

```python
# setup/settings.py
SERVICES_CONFIG = {
    'OPENMIND_AI_URL': 'http://127.0.0.1:8000',
    'PRODUCT_SERVICE_URL': 'http://127.0.0.1:8001',
    'CREWAI_SERVICE_URL': 'http://127.0.0.1:8002',
    'AGNOS_SERVICE_URL': 'http://127.0.0.1:8003',
    'EVOLUTION_API_URL': 'http://127.0.0.1:8004',
    'EVOLUTION_API_KEY': 'GKvy6psn-8HHpBQ4HAHKFOXnwjHR-oSzeGZzCaws0xg',
    'EVOLUTION_WEBHOOK_URL': 'http://69.169.102.84:5000/api/webhooks/evolution/',
    # MCP Server (para Claude Desktop)
    'MCP_SERVER_MODULE': 'mcp_server_sinapum',
}
```

---

## 🚀 Plano de Implementação

### Fase 1: Consolidação Atual (Já feito)

- ✅ Django como orquestrador principal
- ✅ OpenMind AI Server (FastAPI) funcionando
- ✅ Evolution API (WhatsApp) funcionando
- ✅ Integração Django → FastAPI via HTTP
- ✅ Integração Django → Evolution API via HTTP
- ✅ Master Control Program (estrutura planejada)

### Fase 2: Model Context Protocol + Novos Serviços (Recomendado)

**Prioridade Máxima:**
1. 🆕 **MCP Server SinapUm** (Protocolo MCP)
   - Implementar servidor MCP oficial
   - Expor tools, resources e prompts
   - Configurar Claude Desktop
   - Integrar com serviços existentes

**Prioridade Alta:**
2. 🆕 **Product Service** (Porta 8001)
   - Gerenciamento de produtos
   - APIs públicas de alta performance
   - Integração com Django ORM

3. 🆕 **CrewAI Service** (Porta 8002)
   - Orquestração de agentes
   - Análise complexa
   - Processamento assíncrono

4. 🆕 **Agnos Service** (Porta 8003)
   - Workflows de alto nível
   - Validação de dados
   - Processamento em pipeline

### Fase 3: Expansão Futura

**Prioridade Média:**
- 🔮 MotoPro Service (Porta 8005)
- 🔮 SparkScore Service (Porta 8006)
- 🔮 KMN Service (Porta 8007)

---

## ✅ Vantagens da Arquitetura

### 1. **Separação de Responsabilidades**
- Django = Orquestração, Admin, ORM
- FastAPI = Serviços especializados, alta performance
- Evolution API = Integração WhatsApp, mensageria
- MCP Server = Interface padronizada para LLMs (Claude Desktop)

### 2. **Escalabilidade**
- Cada serviço pode escalar independentemente
- Django pode ter múltiplas instâncias
- FastAPI pode ter múltiplas instâncias
- Load balancing por serviço

### 3. **Manutenibilidade**
- Código organizado por serviço
- Fácil de testar cada serviço isoladamente
- Fácil de adicionar novos serviços

### 4. **Performance**
- FastAPI assíncrono para operações pesadas
- Django para operações que precisam de ORM/Admin
- Melhor dos dois mundos

### 5. **Flexibilidade**
- Pode adicionar novos serviços sem quebrar existentes
- Pode migrar serviços gradualmente
- Pode usar diferentes tecnologias por serviço

---

## 🔒 Segurança

### Recomendações

1. **Autenticação entre serviços:**
   ```python
   # API Keys ou JWT tokens
   headers = {
       'Authorization': f'Bearer {SERVICE_API_KEY}'
   }
   ```

2. **HTTPS em produção:**
   - Todos os serviços devem usar HTTPS
   - Certificados SSL/TLS

3. **Rate limiting:**
   - Implementar rate limiting em cada serviço
   - Proteção contra DDoS

4. **Validação de entrada:**
   - Pydantic no FastAPI (automático)
   - Validação manual no Django

---

## 📈 Monitoramento

### Recomendações

1. **Health checks:**
   - Cada serviço deve ter `/health`
   - Django verifica saúde dos serviços

2. **Logs centralizados:**
   - Loki/Grafana (já configurado)
   - Logs estruturados (JSON)

3. **Métricas:**
   - Prometheus (futuro)
   - Métricas por serviço

4. **Telemetria:**
   - Master Control Program registra todas as execuções
   - Tempo de resposta por serviço
   - Taxa de erro por serviço

---

## 🧪 Testes

### Estratégia de Testes

1. **Testes unitários:**
   - Cada serviço testado isoladamente
   - Django: testes de views, models
   - FastAPI: testes de endpoints

2. **Testes de integração:**
   - Testar comunicação Django → FastAPI
   - Testar fluxo completo

3. **Testes end-to-end:**
   - Testar fluxo completo do cliente até resposta

---

## 📚 Documentação

### Recomendações

1. **Documentação de API:**
   - FastAPI: Swagger automático (`/docs`)
   - Django: Documentação manual ou drf-yasg

2. **Documentação de arquitetura:**
   - Este documento
   - Diagramas atualizados

3. **Documentação de serviços:**
   - README por serviço
   - Exemplos de uso

---

## 🎯 Conclusão

### Arquitetura Recomendada

**Django + FastAPI + Evolution API + Model Context Protocol = Arquitetura Completa**

- ✅ **Django** para orquestração, admin, ORM
- ✅ **FastAPI** para serviços especializados, alta performance
- ✅ **Evolution API** para integração WhatsApp, mensageria
- ✅ **Model Context Protocol** para integração oficial com Claude Desktop e LLMs
- ✅ **Integração via HTTP** simples e eficiente
- ✅ **Protocolo MCP** padronizado para LLMs
- ✅ **Escalável** e **manutenível**

### Próximos Passos

1. ✅ Manter Django como orquestrador principal
2. ✅ Evolution API (WhatsApp) já integrado
3. 🆕 **Implementar MCP Server SinapUm** (Prioridade Máxima)
   - Criar estrutura `mcp_server_sinapum/`
   - Implementar tools, resources e prompts
   - Configurar Claude Desktop
4. 🆕 Implementar Product Service (FastAPI)
5. 🆕 Implementar CrewAI Service (FastAPI)
6. 🆕 Implementar Agnos Service (FastAPI)
7. 📈 Monitorar e otimizar
8. 🔗 Melhorar integração WhatsApp com MCP

---

**Última atualização:** 2025-01-13  
**Versão:** 1.0.0  
**Status:** Recomendação Ativa

