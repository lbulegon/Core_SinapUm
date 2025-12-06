# 📱 Como Criar Apps no Django

Guia passo a passo para criar novos apps no projeto Django.

## 🎯 Método Recomendado: Usando o comando `startapp`

### Passo 1: Ativar Ambiente Virtual

```bash
cd /root/SinapUm
source venv/bin/activate
```

**Nota:** Se ainda não criou o venv, execute primeiro:
```bash
python3 -m venv venv
source venv/bin/activate
pip install Django
```

### Passo 2: Navegar para o Projeto

```bash
cd setup
```

### Passo 3: Criar o App

```bash
python manage.py startapp nome_do_app
```

**Exemplos:**
```bash
python manage.py startapp produtos
python manage.py startapp usuarios
python manage.py startapp blog
python manage.py startapp api
```

### Passo 4: Estrutura Criada Automaticamente

O comando `startapp` cria automaticamente:

```
nome_do_app/
├── __init__.py          # Torna o diretório um pacote Python
├── admin.py             # Configuração do admin Django
├── apps.py              # Configuração do app
├── models.py            # Modelos de banco de dados
├── tests.py             # Testes unitários
└── views.py             # Views (lógica de negócio)
```

## ⚙️ Configurar o App no Django

### 1. Adicionar ao INSTALLED_APPS

Editar `/root/SinapUm/setup/setup/settings.py`:

```python
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'home',              # App já existente
    'nome_do_app',       # ✅ Adicionar o novo app aqui
]
```

### 2. Criar URLs do App

Criar arquivo `nome_do_app/urls.py`:

```python
from django.urls import path
from . import views

app_name = 'nome_do_app'

urlpatterns = [
    path('', views.index, name='index'),
]
```

### 3. Criar Views Básicas

Editar `nome_do_app/views.py`:

```python
from django.shortcuts import render
from django.http import HttpResponse

def index(request):
    return HttpResponse('Olá! Esta é a página do app.')
```

### 4. Incluir URLs no Projeto Principal

Editar `/root/SinapUm/setup/setup/urls.py`:

```python
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('home.urls')),
    path('nome_do_app/', include('nome_do_app.urls')),  # ✅ Adicionar
]
```

## 📁 Estrutura Completa de um App

Depois de criar o app, você pode adicionar:

```
nome_do_app/
├── __init__.py
├── admin.py
├── apps.py
├── models.py
├── views.py
├── urls.py                 # ✅ Criar manualmente
├── forms.py                # ✅ Criar manualmente (opcional)
├── tests.py
├── migrations/             # Criado automaticamente quando criar models
│   └── __init__.py
├── templates/              # ✅ Criar manualmente
│   └── nome_do_app/
│       └── index.html
└── static/                 # ✅ Criar manualmente
    └── nome_do_app/
        ├── css/
        ├── js/
        └── img/
```

## 🎯 Exemplo Prático: Criar App "Produtos"

### 1. Criar o App

```bash
cd /root/SinapUm/setup
source ../venv/bin/activate
python manage.py startapp produtos
```

### 2. Adicionar ao settings.py

```python
INSTALLED_APPS = [
    # ... outros apps
    'home',
    'produtos',  # ✅ Adicionar
]
```

### 3. Criar URLs

Criar `produtos/urls.py`:

```python
from django.urls import path
from . import views

app_name = 'produtos'

urlpatterns = [
    path('', views.lista, name='lista'),
    path('<int:id>/', views.detalhe, name='detalhe'),
]
```

### 4. Criar Views

Editar `produtos/views.py`:

```python
from django.shortcuts import render
from django.http import HttpResponse

def lista(request):
    return render(request, 'produtos/lista.html')

def detalhe(request, id):
    return HttpResponse(f'Detalhe do produto {id}')
```

### 5. Criar Templates

```bash
mkdir -p produtos/templates/produtos
```

Criar `produtos/templates/produtos/lista.html`:

```html
<!DOCTYPE html>
<html>
<head>
    <title>Lista de Produtos</title>
</head>
<body>
    <h1>Produtos</h1>
    <p>Lista de produtos aqui...</p>
</body>
</html>
```

### 6. Incluir URLs no Projeto

Editar `setup/urls.py`:

```python
urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('home.urls')),
    path('produtos/', include('produtos.urls')),  # ✅ Novo app
]
```

### 7. Testar

Acessar: http://69.169.102.84/produtos/

## 🔧 Comandos Úteis

### Criar App
```bash
python manage.py startapp nome_do_app
```

### Verificar Apps Instalados
```bash
python manage.py check
```

### Ver Estrutura do Projeto
```bash
tree -L 2  # Se tiver tree instalado
# ou
find . -type d -name "__pycache__" -prune -o -type f -print
```

## 📋 Checklist ao Criar Novo App

- [ ] Criar app: `python manage.py startapp nome_do_app`
- [ ] Adicionar ao `INSTALLED_APPS` em `settings.py`
- [ ] Criar `urls.py` no app
- [ ] Criar views básicas em `views.py`
- [ ] Incluir URLs no `urls.py` principal
- [ ] Criar templates (se necessário)
- [ ] Criar diretório `static/` (se necessário)
- [ ] Testar o app

## 🎓 App Já Criado: `home`

Você já tem um app `home` criado como exemplo:

- **Localização:** `/root/SinapUm/setup/home/`
- **Função:** Página inicial do servidor
- **URLs:** `/` (raiz)
- **Estrutura completa:**
  - ✅ `views.py` - Views criadas
  - ✅ `urls.py` - URLs configuradas
  - ✅ `templates/home/` - Templates HTML
  - ✅ `static/home/` - Arquivos estáticos
  - ✅ Adicionado ao `INSTALLED_APPS`

Use o app `home` como referência para criar outros apps!

## 🚀 Comandos Rápidos

```bash
# Ativar ambiente virtual
cd /root/SinapUm
source venv/bin/activate

# Criar novo app
cd setup
python manage.py startapp nome_do_app

# Editar settings.py para adicionar ao INSTALLED_APPS
# Criar urls.py no app
# Incluir URLs no projeto principal
# Testar!
```

## 📚 Próximos Passos Após Criar App

1. **Criar Models** (se usar banco de dados):
   ```bash
   python manage.py makemigrations nome_do_app
   python manage.py migrate
   ```

2. **Criar Templates HTML**

3. **Criar Forms** (para formulários)

4. **Configurar Admin** (para painel administrativo)

5. **Adicionar Estilos CSS**

6. **Adicionar JavaScript** (se necessário)


