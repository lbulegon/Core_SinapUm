# 🔗 Integração Django + FastAPI no MCP_SinapUm

**Data:** 2025-01-13  
**Objetivo:** Explicar como integrar Django e FastAPI no projeto MCP_SinapUm

---

## ✅ Resposta Rápida

**Sim!** É possível e **já está parcialmente implementado**:

- ✅ **Django** = SinapUm (orquestrador principal)
- ✅ **FastAPI** = OpenMind AI Server (serviço especializado)
- ✅ **Integração** = Django chama FastAPI via HTTP

**E podemos melhorar ainda mais!**

---

## 🏗️ Arquitetura Atual

### Situação Atual

```
┌─────────────────────────────────────────┐
│  Cliente (VitrineZap, etc.)             │
└──────────────┬──────────────────────────┘
               │ HTTP
               ▼
┌─────────────────────────────────────────┐
│  SinapUm (Django)                        │
│  - Porta: 5000                           │
│  - Views, Models, Admin                  │
│  - Master Control Program (interno)       │
└──────────────┬──────────────────────────┘
               │ HTTP Request
               ▼
┌─────────────────────────────────────────┐
│  OpenMind AI Server (FastAPI)            │
│  - Porta: 8000                           │
│  - Análise de imagens                    │
│  - Alta performance                      │
└─────────────────────────────────────────┘
```

**Status:** ✅ Já funciona assim!

---

## 🔄 Como Funciona a Integração Atual

### Django chamando FastAPI

```python
# app_sinapum/services.py
import requests
from django.conf import settings

OPENMIND_AI_URL = getattr(settings, 'OPENMIND_AI_URL', 'http://127.0.0.1:8000')

def analyze_image_with_openmind(image_file, image_path=None, image_url=None):
    """
    Analisa uma imagem usando o OpenMind AI Server (FastAPI).
    
    Django → HTTP Request → FastAPI → Resposta
    """
    url = f"{OPENMIND_AI_URL}/api/v1/analyze-product-image"
    
    files = {
        'image': (image_file.name, image_file.read(), image_file.content_type)
    }
    
    # Django faz requisição HTTP para FastAPI
    response = requests.post(url, files=files, timeout=60)
    
    if response.status_code == 200:
        return response.json()  # Resposta do FastAPI
    else:
        raise Exception(f"Erro ao chamar OpenMind: {response.status_code}")
```

**Fluxo:**
1. Cliente chama Django (`/api/v1/analyze-product-image`)
2. Django recebe a imagem
3. Django faz HTTP request para FastAPI (`http://127.0.0.1:8000/api/v1/analyze-product-image`)
4. FastAPI processa (análise de imagem)
5. FastAPI retorna JSON
6. Django retorna resposta para o cliente

---

## 🚀 Melhorias Possíveis

### 1. Adicionar Mais Serviços FastAPI

Podemos criar **novos serviços FastAPI** especializados:

```
┌─────────────────────────────────────────┐
│  SinapUm (Django) - Orquestrador        │
└───┬─────────────────────────────────────┘
    │
    ├──→ OpenMind AI (FastAPI) - Análise de imagens
    ├──→ CrewAI Service (FastAPI) - Orquestração de agentes
    ├──→ Agnos Service (FastAPI) - Workflows
    └──→ Product Service (FastAPI) - Gerenciamento de produtos
```

**Vantagens:**
- ✅ Cada serviço é independente
- ✅ Pode escalar separadamente
- ✅ Alta performance em cada serviço
- ✅ Fácil de manter e testar

### 2. FastAPI como Gateway/Proxy

Podemos usar **FastAPI como gateway** na frente do Django:

```
┌─────────────────────────────────────────┐
│  Cliente                                 │
└──────────────┬──────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────┐
│  FastAPI Gateway (Porta 80)              │
│  - Rate limiting                         │
│  - Autenticação                          │
│  - Load balancing                        │
│  - Cache                                 │
└──────────────┬──────────────────────────┘
               │
               ├──→ SinapUm Django (Porta 5000)
               ├──→ OpenMind AI (Porta 8000)
               └──→ Outros serviços
```

**Vantagens:**
- ✅ FastAPI como entrada (alta performance)
- ✅ Roteamento inteligente
- ✅ Cache e rate limiting
- ✅ Django continua funcionando normalmente

### 3. FastAPI para APIs Públicas

Podemos expor **APIs públicas via FastAPI** e manter Django para admin:

```
┌─────────────────────────────────────────┐
│  Clientes Externos                       │
└──────────────┬──────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────┐
│  FastAPI (Porta 80) - APIs Públicas     │
│  - /api/v1/products                      │
│  - /api/v1/analyze                       │
│  - Alta performance                       │
└──────────────┬──────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────┐
│  Django (Porta 5000) - Sistema Interno  │
│  - Admin                                 │
│  - Models                                │
│  - ORM                                   │
└─────────────────────────────────────────┘
```

**Vantagens:**
- ✅ APIs públicas rápidas (FastAPI)
- ✅ Admin e sistema interno (Django)
- ✅ Melhor dos dois mundos

---

## 💻 Exemplos Práticos de Integração

### Exemplo 1: Criar Serviço FastAPI para Produtos

```python
# product_service/main.py (Novo serviço FastAPI)
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List
import httpx

app = FastAPI(title="Product Service")

class ProductCreate(BaseModel):
    name: str
    price: float
    description: str

class ProductResponse(BaseModel):
    id: int
    name: str
    price: float
    description: str

@app.post("/api/products/", response_model=ProductResponse)
async def create_product(product: ProductCreate):
    """Criar produto (FastAPI)"""
    # Pode chamar Django via HTTP ou acessar banco diretamente
    # Exemplo: chamar Django
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "http://127.0.0.1:5000/api/internal/products/",
            json=product.dict()
        )
        return response.json()

@app.get("/api/products/", response_model=List[ProductResponse])
async def list_products():
    """Listar produtos (FastAPI)"""
    async with httpx.AsyncClient() as client:
        response = await client.get("http://127.0.0.1:5000/api/internal/products/")
        return response.json()
```

**Django recebe:**
```python
# app_sinapum/views.py
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import Product

@csrf_exempt
def api_internal_create_product(request):
    """Endpoint interno para FastAPI chamar"""
    data = json.loads(request.body)
    product = Product.objects.create(
        name=data['name'],
        price=data['price'],
        description=data['description']
    )
    return JsonResponse({
        'id': product.id,
        'name': product.name,
        'price': float(product.price),
        'description': product.description
    })
```

### Exemplo 2: FastAPI como Gateway

```python
# gateway/main.py (FastAPI Gateway)
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
import httpx

app = FastAPI(title="SinapUm Gateway")

# Configuração de serviços
SERVICES = {
    'django': 'http://127.0.0.1:5000',
    'openmind': 'http://127.0.0.1:8000',
    'products': 'http://127.0.0.1:8001',
}

@app.post("/api/v1/analyze-product-image")
async def analyze_image(request: Request):
    """Gateway para análise de imagem"""
    # Recebe requisição
    form_data = await request.form()
    
    # Roteia para OpenMind (FastAPI)
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{SERVICES['openmind']}/api/v1/analyze-product-image",
            files=dict(form_data)
        )
        return JSONResponse(content=response.json())

@app.get("/api/v1/products/")
async def list_products():
    """Gateway para listar produtos"""
    # Roteia para Product Service (FastAPI)
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{SERVICES['products']}/api/products/")
        return JSONResponse(content=response.json())

@app.get("/admin/")
async def admin_redirect():
    """Redireciona admin para Django"""
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{SERVICES['django']}/admin/")
        return response
```

### Exemplo 3: Django chamando múltiplos FastAPIs

```python
# app_sinapum/services.py
import httpx
from django.conf import settings

async def analyze_with_multiple_services(image_file):
    """
    Chama múltiplos serviços FastAPI em paralelo
    """
    async with httpx.AsyncClient() as client:
        # Chamar múltiplos serviços em paralelo
        tasks = [
            client.post(
                "http://127.0.0.1:8000/api/v1/analyze-product-image",
                files={'image': image_file}
            ),
            client.post(
                "http://127.0.0.1:8001/api/v1/enrich-product",
                files={'image': image_file}
            ),
            client.post(
                "http://127.0.0.1:8002/api/v1/validate-product",
                files={'image': image_file}
            ),
        ]
        
        # Executar em paralelo (async)
        responses = await asyncio.gather(*tasks)
        
        # Combinar resultados
        results = [r.json() for r in responses]
        
        return {
            'analysis': results[0],
            'enrichment': results[1],
            'validation': results[2],
        }
```

---

## 🎯 Arquitetura Híbrida Recomendada

### Opção 1: Django Principal + FastAPI Serviços

```
┌─────────────────────────────────────────┐
│  Cliente                                 │
└──────────────┬──────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────┐
│  SinapUm Django (Porta 5000)            │
│  - Orquestrador principal               │
│  - Admin, Models, ORM                   │
│  - Master Control Program               │
└───┬─────────────────────────────────────┘
    │
    ├──→ OpenMind AI (FastAPI:8000) - Análise
    ├──→ Product Service (FastAPI:8001) - Produtos
    ├──→ CrewAI Service (FastAPI:8002) - Agentes
    └──→ Agnos Service (FastAPI:8003) - Workflows
```

**Vantagens:**
- ✅ Django como orquestrador (familiar)
- ✅ FastAPI para serviços especializados (performance)
- ✅ Cada serviço é independente
- ✅ Fácil de escalar

### Opção 2: FastAPI Gateway + Django Backend

```
┌─────────────────────────────────────────┐
│  Cliente                                 │
└──────────────┬──────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────┐
│  FastAPI Gateway (Porta 80)             │
│  - Rate limiting                        │
│  - Cache                                 │
│  - Autenticação                         │
│  - Roteamento                           │
└───┬─────────────────────────────────────┘
    │
    ├──→ SinapUm Django (5000) - Admin, ORM
    ├──→ OpenMind AI (8000) - Análise
    └──→ Outros serviços
```

**Vantagens:**
- ✅ FastAPI como entrada (alta performance)
- ✅ Django para admin e ORM
- ✅ Cache e rate limiting no gateway
- ✅ Roteamento inteligente

### Opção 3: FastAPI APIs Públicas + Django Interno

```
┌─────────────────────────────────────────┐
│  Clientes Externos                      │
└──────────────┬──────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────┐
│  FastAPI (Porta 80) - APIs Públicas    │
│  - /api/v1/products                     │
│  - /api/v1/analyze                      │
│  - Alta performance                     │
└──────────────┬──────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────┐
│  Django (Porta 5000) - Sistema Interno │
│  - /admin/                              │
│  - Models, ORM                          │
│  - Master Control Program               │
└─────────────────────────────────────────┘
```

**Vantagens:**
- ✅ APIs públicas rápidas (FastAPI)
- ✅ Admin e sistema interno (Django)
- ✅ Separação clara de responsabilidades

---

## 🔧 Implementação Prática

### Passo 1: Criar Serviço FastAPI Adicional

```bash
# Criar novo serviço FastAPI
mkdir -p /root/MCP_SinapUm/services/product_service
cd /root/MCP_SinapUm/services/product_service

# Criar estrutura
touch main.py requirements.txt
```

```python
# services/product_service/main.py
from fastapi import FastAPI
import httpx

app = FastAPI(title="Product Service")

@app.get("/api/products/")
async def list_products():
    """Listar produtos - chama Django"""
    async with httpx.AsyncClient() as client:
        response = await client.get("http://127.0.0.1:5000/api/internal/products/")
        return response.json()
```

### Passo 2: Django Expõe Endpoints Internos

```python
# app_sinapum/views.py
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import Product

@csrf_exempt
def api_internal_list_products(request):
    """Endpoint interno para FastAPI chamar"""
    products = Product.objects.all()
    return JsonResponse({
        'products': [
            {
                'id': p.id,
                'name': p.name,
                'price': float(p.price)
            }
            for p in products
        ]
    })
```

### Passo 3: Configurar URLs

```python
# setup/urls.py
urlpatterns = [
    # ... rotas existentes
    path('api/internal/products/', views.api_internal_list_products),
]
```

---

## 📊 Comparação: Integração vs Não Integração

### Sem Integração (Apenas Django)

```
Cliente → Django → Tudo no Django
```

**Limitações:**
- ❌ Performance limitada (síncrono)
- ❌ Tudo acoplado
- ❌ Difícil escalar partes específicas

### Com Integração (Django + FastAPI)

```
Cliente → Django → FastAPI (serviços especializados)
```

**Vantagens:**
- ✅ Alta performance (FastAPI assíncrono)
- ✅ Serviços independentes
- ✅ Fácil escalar cada serviço
- ✅ Melhor dos dois mundos

---

## ✅ Recomendações para MCP_SinapUm

### Estratégia Recomendada

1. **Manter Django como orquestrador principal**
   - ✅ Admin, Models, ORM
   - ✅ Master Control Program
   - ✅ Sistema interno

2. **Usar FastAPI para serviços especializados**
   - ✅ OpenMind AI (já existe)
   - ✅ Novos serviços de alta performance
   - ✅ APIs públicas

3. **Integração via HTTP**
   - ✅ Django chama FastAPI via `requests` ou `httpx`
   - ✅ Cada serviço é independente
   - ✅ Fácil de escalar

### Arquitetura Ideal

```
┌─────────────────────────────────────────┐
│  Cliente (VitrineZap, etc.)             │
└──────────────┬──────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────┐
│  SinapUm Django (Porta 5000)           │
│  - Orquestrador principal              │
│  - Admin, Models, ORM                  │
│  - Master Control Program              │
└───┬─────────────────────────────────────┘
    │
    ├──→ OpenMind AI (FastAPI:8000) ✅ Já existe
    ├──→ Product Service (FastAPI:8001) 🆕 Futuro
    ├──→ CrewAI Service (FastAPI:8002) 🆕 Futuro
    └──→ Agnos Service (FastAPI:8003) 🆕 Futuro
```

---

## 🎓 Conclusão

### Resposta à Pergunta

**"Django atende bem, mas poderíamos integrar com FastAPI?"**

**Sim! E já está parcialmente feito:**

1. ✅ **Django** = Orquestrador principal (SinapUm)
2. ✅ **FastAPI** = Serviço especializado (OpenMind AI)
3. ✅ **Integração** = Django chama FastAPI via HTTP

### Próximos Passos

1. **Manter Django** como orquestrador principal
2. **Criar novos serviços FastAPI** para partes que precisam de alta performance
3. **Integrar via HTTP** (requests/httpx)
4. **Escalar independentemente** cada serviço

### Benefícios

- ✅ Django para o que faz bem (admin, ORM, sistema completo)
- ✅ FastAPI para o que precisa de performance (APIs, serviços)
- ✅ Melhor dos dois mundos
- ✅ Arquitetura moderna e escalável

---

**Última atualização:** 2025-01-13

