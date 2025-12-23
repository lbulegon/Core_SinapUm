# 🔍 Django vs FastAPI: Comparação Completa

**Data:** 2025-01-13  
**Objetivo:** Explicar as diferenças fundamentais entre Django e FastAPI

---

## 📊 Resumo Executivo

| Aspecto | Django | FastAPI |
|---------|--------|---------|
| **Tipo** | Framework web completo (full-stack) | Framework web moderno (API-first) |
| **Foco** | Aplicações web completas | APIs REST modernas |
| **Estilo** | Síncrono (tradicional) | Assíncrono (moderno) |
| **Complexidade** | Mais complexo, mais recursos | Mais simples, focado |
| **Melhor para** | Sites completos, admin, CMS | APIs, microserviços, alta performance |
| **Ano de lançamento** | 2005 | 2018 |

---

## 🎯 O que são?

### Django

**Django** é um **framework web completo** (full-stack) para Python, criado em 2005.

**Características:**
- ✅ Framework "baterias incluídas" (tudo que precisa já vem)
- ✅ ORM (Object-Relational Mapping) integrado
- ✅ Sistema de templates
- ✅ Admin automático
- ✅ Sistema de autenticação
- ✅ Migrações de banco de dados
- ✅ Sistema de roteamento
- ✅ Middleware
- ✅ Formulários
- ✅ Sessões

**Filosofia:** "Baterias incluídas" - tudo que você precisa já está lá.

### FastAPI

**FastAPI** é um **framework web moderno** para Python, criado em 2018.

**Características:**
- ✅ Focado em APIs REST
- ✅ Assíncrono (async/await)
- ✅ Alta performance
- ✅ Validação automática de tipos (Pydantic)
- ✅ Documentação automática (Swagger/OpenAPI)
- ✅ Type hints nativos
- ✅ Baseado em padrões modernos (OpenAPI, JSON Schema)

**Filosofia:** "Moderno, rápido, focado em APIs"

---

## 🏗️ Arquitetura

### Django - Arquitetura Tradicional

```
Django App
├── Models (ORM)          # Banco de dados
├── Views (Controllers)    # Lógica de negócio
├── Templates (HTML)       # Interface
├── URLs (Routing)         # Rotas
├── Forms                  # Formulários
├── Admin                  # Interface administrativa
└── Middleware             # Processamento de requisições
```

**Padrão:** MVC (Model-View-Controller) / MTV (Model-Template-View)

### FastAPI - Arquitetura Moderna

```
FastAPI App
├── Routes (Endpoints)     # Rotas/Endpoints
├── Models (Pydantic)      # Validação de dados
├── Dependencies           # Injeção de dependências
└── Background Tasks       # Tarefas assíncronas
```

**Padrão:** Baseado em funções assíncronas e type hints

---

## 💻 Comparação de Código

### Exemplo 1: Criar um Endpoint Simples

#### Django

```python
# views.py
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
import json

@csrf_exempt
@require_http_methods(["POST"])
def create_user(request):
    """Criar usuário"""
    try:
        data = json.loads(request.body)
        name = data.get('name')
        email = data.get('email')
        
        # Validação manual
        if not name or not email:
            return JsonResponse(
                {'error': 'Name and email are required'},
                status=400
            )
        
        # Criar usuário (exemplo)
        user = User.objects.create(name=name, email=email)
        
        return JsonResponse({
            'id': user.id,
            'name': user.name,
            'email': user.email
        }, status=201)
    
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

# urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('api/users/', views.create_user, name='create_user'),
]
```

**Características:**
- ❌ Validação manual
- ❌ Parse JSON manual
- ❌ Tratamento de erros manual
- ✅ Funciona, mas verboso

#### FastAPI

```python
# main.py
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, EmailStr
from typing import Optional

app = FastAPI()

# Model com validação automática
class UserCreate(BaseModel):
    name: str
    email: EmailStr  # Validação automática de email

class UserResponse(BaseModel):
    id: int
    name: str
    email: str

@app.post("/api/users/", response_model=UserResponse, status_code=201)
async def create_user(user: UserCreate):
    """Criar usuário"""
    # Validação automática via Pydantic
    # user.name e user.email já estão validados
    
    # Criar usuário (exemplo)
    user_obj = User(name=user.name, email=user.email)
    user_obj.save()
    
    return UserResponse(
        id=user_obj.id,
        name=user_obj.name,
        email=user_obj.email
    )
```

**Características:**
- ✅ Validação automática (Pydantic)
- ✅ Type hints
- ✅ Documentação automática
- ✅ Código mais limpo

---

### Exemplo 2: Listar Dados com Filtros

#### Django

```python
# views.py
from django.http import JsonResponse
from django.core.paginator import Paginator

def list_users(request):
    """Listar usuários com filtros"""
    # Parse de query parameters manual
    page = int(request.GET.get('page', 1))
    limit = int(request.GET.get('limit', 10))
    search = request.GET.get('search', '')
    
    # Query
    users = User.objects.all()
    
    if search:
        users = users.filter(name__icontains=search)
    
    # Paginação manual
    paginator = Paginator(users, limit)
    page_obj = paginator.get_page(page)
    
    # Serialização manual
    users_data = [
        {
            'id': user.id,
            'name': user.name,
            'email': user.email
        }
        for user in page_obj
    ]
    
    return JsonResponse({
        'users': users_data,
        'page': page,
        'total_pages': paginator.num_pages,
        'total': paginator.count
    })
```

#### FastAPI

```python
# main.py
from fastapi import FastAPI, Query
from typing import Optional
from pydantic import BaseModel

app = FastAPI()

class UserResponse(BaseModel):
    id: int
    name: str
    email: str

@app.get("/api/users/", response_model=list[UserResponse])
async def list_users(
    page: int = Query(1, ge=1),  # ge=1 significa >= 1
    limit: int = Query(10, ge=1, le=100),  # entre 1 e 100
    search: Optional[str] = Query(None, min_length=1)
):
    """Listar usuários com filtros"""
    # Query
    users = User.objects.all()
    
    if search:
        users = users.filter(name__icontains=search)
    
    # Paginação (exemplo simplificado)
    start = (page - 1) * limit
    end = start + limit
    users_page = users[start:end]
    
    # Serialização automática via Pydantic
    return [
        UserResponse(id=u.id, name=u.name, email=u.email)
        for u in users_page
    ]
```

**Vantagens do FastAPI:**
- ✅ Validação automática de query parameters
- ✅ Type hints claros
- ✅ Documentação automática no Swagger
- ✅ Código mais declarativo

---

## ⚡ Performance

### Django

- **Síncrono:** Uma requisição por thread
- **Performance:** Boa para aplicações tradicionais
- **Escalabilidade:** Vertical (mais servidores)
- **Melhor para:** Aplicações web completas, CMS, sites

**Exemplo de uso:**
- Sites corporativos
- Blogs
- E-commerce
- Sistemas administrativos
- Aplicações com interface web completa

### FastAPI

- **Assíncrono:** Múltiplas requisições simultâneas
- **Performance:** Muito alta (comparable a Node.js e Go)
- **Escalabilidade:** Horizontal (múltiplas instâncias)
- **Melhor para:** APIs, microserviços, alta concorrência

**Exemplo de uso:**
- APIs REST
- Microserviços
- Backend para apps mobile
- Integrações entre sistemas
- Serviços de alta performance

**Benchmark (requests/segundo):**
- Django: ~5.000-10.000 req/s
- FastAPI: ~20.000-50.000 req/s (com async)

---

## 🗄️ Banco de Dados

### Django - ORM Integrado

```python
# models.py
from django.db import models

class User(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

# Uso
user = User.objects.create(name="João", email="joao@email.com")
users = User.objects.filter(name__icontains="João")
user = User.objects.get(id=1)
user.delete()
```

**Características:**
- ✅ ORM completo integrado
- ✅ Migrações automáticas
- ✅ Suporte a múltiplos bancos
- ✅ Queries complexas
- ✅ Admin automático

### FastAPI - Flexível

```python
# FastAPI não tem ORM próprio, você escolhe:

# Opção 1: SQLAlchemy (mais comum)
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    name = Column(String(100))
    email = Column(String(100), unique=True)

# Opção 2: Databases (async)
from databases import Database

database = Database("postgresql://...")

# Opção 3: SQL direto
# Opção 4: MongoDB, Redis, etc.
```

**Características:**
- ✅ Flexibilidade total
- ✅ Você escolhe o ORM/banco
- ✅ Suporte a async nativo
- ❌ Mais configuração necessária

---

## 📚 Documentação Automática

### Django

```python
# Não tem documentação automática
# Precisa escrever manualmente ou usar ferramentas externas
# Exemplo: django-rest-framework tem Swagger, mas não é nativo
```

### FastAPI

```python
# Documentação automática incluída!

# Acesse automaticamente:
# - http://localhost:8000/docs (Swagger UI)
# - http://localhost:8000/redoc (ReDoc)

# Tudo gerado automaticamente a partir do código!
```

**Exemplo:**
```python
@app.post("/api/users/", response_model=UserResponse)
async def create_user(user: UserCreate):
    """Criar um novo usuário"""
    pass

# FastAPI gera automaticamente:
# - Documentação Swagger
# - Schema JSON
# - Exemplos de requisição/resposta
# - Validação de tipos
```

---

## 🔒 Autenticação e Segurança

### Django

```python
# Sistema completo de autenticação
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User

@login_required
def protected_view(request):
    return JsonResponse({'user': request.user.username})

# Middleware de autenticação
# CSRF protection automático
# Password hashing
# Sessions
```

**Características:**
- ✅ Sistema completo integrado
- ✅ CSRF protection automático
- ✅ Password hashing seguro
- ✅ Sessions
- ✅ Permissões e grupos

### FastAPI

```python
# Você implementa ou usa bibliotecas
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

async def get_current_user(token: str = Depends(oauth2_scheme)):
    # Validação manual
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=401)
    except JWTError:
        raise HTTPException(status_code=401)
    return username

@app.get("/protected")
async def protected_route(current_user: str = Depends(get_current_user)):
    return {"user": current_user}
```

**Características:**
- ✅ Flexibilidade total
- ✅ Você escolhe a estratégia
- ❌ Mais código para escrever
- ✅ Suporte a OAuth2, JWT, etc.

---

## 🎨 Templates e Interface

### Django

```python
# Sistema completo de templates
# templates/users/list.html
{% extends "base.html" %}
{% block content %}
    <h1>Usuários</h1>
    {% for user in users %}
        <p>{{ user.name }} - {{ user.email }}</p>
    {% endfor %}
{% endblock %}

# views.py
def list_users(request):
    users = User.objects.all()
    return render(request, 'users/list.html', {'users': users})
```

**Características:**
- ✅ Sistema de templates completo
- ✅ Herança de templates
- ✅ Tags e filtros customizados
- ✅ Forms integrados
- ✅ Admin automático

### FastAPI

```python
# Não tem sistema de templates nativo
# Você usa frameworks frontend separados:
# - React, Vue, Angular (SPA)
# - Jinja2 (se quiser templates)
# - HTML direto (se necessário)

from fastapi.responses import HTMLResponse

@app.get("/", response_class=HTMLResponse)
async def home():
    return """
    <html>
        <body>
            <h1>Hello World</h1>
        </body>
    </html>
    """
```

**Características:**
- ✅ Focado em APIs (JSON)
- ✅ Frontend separado (React, Vue, etc.)
- ❌ Não tem sistema de templates integrado
- ✅ Mais flexível para arquitetura moderna

---

## 📦 Ecossistema

### Django

**Pacotes populares:**
- `django-rest-framework` - APIs REST
- `django-cors-headers` - CORS
- `django-filter` - Filtros
- `django-debug-toolbar` - Debug
- `django-admin` - Admin customizado
- `django-allauth` - Autenticação social

**Ecossistema:**
- ✅ Muito maduro (2005)
- ✅ Muitos pacotes disponíveis
- ✅ Comunidade grande
- ✅ Documentação extensa

### FastAPI

**Pacotes populares:**
- `pydantic` - Validação (já incluído)
- `uvicorn` - Servidor ASGI
- `sqlalchemy` - ORM
- `databases` - Async database
- `python-jose` - JWT
- `python-multipart` - Upload de arquivos

**Ecossistema:**
- ✅ Moderno e crescente
- ✅ Focado em performance
- ✅ Compatível com async/await
- ✅ Documentação excelente

---

## 🎯 Quando Usar Cada Um?

### Use Django quando:

1. ✅ **Aplicação web completa** com interface
2. ✅ **Admin automático** necessário
3. ✅ **Sistema de templates** necessário
4. ✅ **ORM completo** necessário
5. ✅ **Autenticação complexa** (usuários, grupos, permissões)
6. ✅ **CMS ou blog**
7. ✅ **E-commerce**
8. ✅ **Sistema administrativo**
9. ✅ **Projeto grande e complexo**

**Exemplos:**
- Site corporativo
- Blog
- E-commerce
- Sistema de gestão
- Portal administrativo
- CMS

### Use FastAPI quando:

1. ✅ **API REST** pura
2. ✅ **Alta performance** necessária
3. ✅ **Microserviços**
4. ✅ **Backend para mobile/app**
5. ✅ **Integração entre sistemas**
6. ✅ **Assíncrono** necessário
7. ✅ **Documentação automática** importante
8. ✅ **Type hints** e validação automática
9. ✅ **Projeto moderno** e focado

**Exemplos:**
- API REST
- Microserviço
- Backend para app mobile
- Integração entre sistemas
- Serviço de alta performance
- API GraphQL (com bibliotecas)

---

## 🔄 Pode Usar Ambos?

**Sim!** É comum usar ambos juntos:

```
┌─────────────────┐
│  Frontend       │
│  (React/Vue)    │
└────────┬────────┘
         │ HTTP
         ▼
┌─────────────────┐
│  FastAPI         │
│  (API REST)      │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Django          │
│  (Admin/ORM)     │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Banco de Dados  │
└─────────────────┘
```

**Arquitetura híbrida:**
- **FastAPI** = API pública (alta performance)
- **Django** = Admin, ORM, sistema interno

---

## 📊 Tabela Comparativa Completa

| Característica | Django | FastAPI |
|----------------|--------|---------|
| **Tipo** | Full-stack | API-first |
| **Ano** | 2005 | 2018 |
| **Estilo** | Síncrono | Assíncrono |
| **ORM** | Integrado (Django ORM) | Flexível (você escolhe) |
| **Templates** | ✅ Integrado | ❌ Não tem |
| **Admin** | ✅ Automático | ❌ Não tem |
| **Validação** | Manual/Forms | ✅ Automática (Pydantic) |
| **Documentação** | Manual | ✅ Automática (Swagger) |
| **Type Hints** | Opcional | ✅ Nativo |
| **Performance** | Boa | ✅ Muito alta |
| **Curva de aprendizado** | Média | ✅ Baixa |
| **Comunidade** | ✅ Muito grande | Crescendo |
| **Maturidade** | ✅ Muito maduro | Moderno |
| **Melhor para** | Apps completas | APIs, microserviços |

---

## 🎓 Conclusão

### Django

**É um framework completo** para construir aplicações web do zero ao fim:
- Interface web
- Admin
- Banco de dados
- Autenticação
- Templates
- Tudo incluído

**Ideal para:** Aplicações web completas, sites, CMS, sistemas administrativos

### FastAPI

**É um framework moderno** focado em construir APIs REST de alta performance:
- APIs rápidas
- Validação automática
- Documentação automática
- Assíncrono
- Moderno

**Ideal para:** APIs, microserviços, backends modernos, alta performance

---

## 💡 No Contexto do SinapUm

**Por que Django?**
- ✅ Projeto já é Django
- ✅ Tem models, admin, ORM funcionando
- ✅ Master Control Program reutiliza código existente
- ✅ Zero breaking changes

**Por que não FastAPI?**
- ❌ Quebraria tudo que já existe
- ❌ Perderia Admin Django
- ❌ Perderia ORM Django
- ❌ Teria que reescrever tudo

**Mas o OpenMind usa FastAPI:**
- ✅ É um serviço separado
- ✅ Foi criado do zero
- ✅ Precisa de alta performance
- ✅ É especializado (só análise de imagens)

**Arquitetura ideal:**
```
Cliente → SinapUm (Django) → OpenMind (FastAPI) → Resposta
```

Cada um no seu lugar! 🎯

---

**Última atualização:** 2025-01-13

