# 📚 Como Criar Apps no Django

Guia completo para criar e configurar apps no projeto Django.

## 🎯 O Que é um App Django?

Um **app Django** é um componente modular que agrupa funcionalidades relacionadas. Cada app pode ter:
- Models (banco de dados)
- Views (lógica de negócio)
- Templates (HTML)
- URLs (rotas)
- Forms (formulários)
- Admin (painel administrativo)

## 📋 Método 1: Usando o comando `startapp` (Recomendado)

### 1. Ativar Ambiente Virtual

```bash
cd /root/SinapUm
source venv/bin/activate
```

### 2. Navegar para o Diretório do Projeto

```bash
cd setup
```

### 3. Criar o App

```bash
python manage.py startapp nome_do_app
```

**Exemplo:**
```bash
python manage.py startapp produtos
python manage.py startapp usuarios
python manage.py startapp blog
```

Isso cria a estrutura:
```
nome_do_app/
├── __init__.py
├── admin.py
├── apps.py
├── models.py
├── tests.py
├── views.py
└── migrations/
    └── __init__.py
```

## 📋 Método 2: Criar Manualmente

Se preferir criar manualmente:

### 1. Criar Diretório do App

```bash
cd /root/SinapUm/setup
mkdir nome_do_app
cd nome_do_app
```

### 2. Criar Arquivos Necessários

```bash
# Arquivo __init__.py
touch __init__.py

# Diretório migrations
mkdir migrations
touch migrations/__init__.py

# Outros arquivos
touch admin.py apps.py models.py tests.py views.py urls.py
```

### 3. Configurar apps.py

Editar `nome_do_app/apps.py`:

```python
from django.apps import AppConfig


class NomeDoAppConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'nome_do_app'
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
    'home',  # App existente
    'nome_do_app',  # ✅ Adicionar o novo app aqui
]
```

### 2. Criar URLs do App

Criar `nome_do_app/urls.py`:

```python
from django.urls import path
from . import views

app_name = 'nome_do_app'

urlpatterns = [
    path('', views.index, name='index'),
    # Adicionar outras rotas aqui
]
```

### 3. Incluir URLs no Projeto Principal

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

```
nome_do_app/
├── __init__.py              # Torna o diretório um pacote Python
├── admin.py                 # Configuração do admin Django
├── apps.py                  # Configuração do app
├── models.py                # Modelos de banco de dados
├── views.py                 # Views (lógica de negócio)
├── urls.py                  # URLs do app
├── forms.py                 # Formulários (opcional)
├── tests.py                 # Testes (opcional)
├── migrations/              # Migrações do banco de dados
│   └── __init__.py
├── templates/               # Templates HTML (opcional)
│   └── nome_do_app/
│       └── index.html
├── static/                  # Arquivos estáticos (opcional)
│   └── nome_do_app/
│       ├── css/
│       ├── js/
│       └── img/
└── management/              # Comandos customizados (opcional)
    └── commands/
```

## 🎯 Exemplo Prático: Criar App "Produtos"

### 1. Criar o App

```bash
cd /root/SinapUm/setup
source ../venv/bin/activate
python manage.py startapp produtos
```

### 2. Estrutura Criada

```
produtos/
├── __init__.py
├── admin.py
├── apps.py
├── models.py
├── tests.py
└── views.py
```

### 3. Criar Arquivos Adicionais

```bash
cd produtos
mkdir -p templates/produtos static/produtos/{css,js,img}
touch urls.py forms.py
```

### 4. Configurar apps.py

```python
from django.apps import AppConfig


class ProdutosConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'produtos'
```

### 5. Adicionar ao settings.py

```python
INSTALLED_APPS = [
    # ... apps padrão
    'home',
    'produtos',  # ✅ Novo app
]
```

### 6. Criar URLs

`produtos/urls.py`:

```python
from django.urls import path
from . import views

app_name = 'produtos'

urlpatterns = [
    path('', views.lista_produtos, name='lista'),
    path('<int:id>/', views.detalhe_produto, name='detalhe'),
]
```

### 7. Incluir no urls.py Principal

`setup/urls.py`:

```python
urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('home.urls')),
    path('produtos/', include('produtos.urls')),  # ✅ Novo app
]
```

### 8. Criar Views

`produtos/views.py`:

```python
from django.shortcuts import render
from django.http import HttpResponse

def lista_produtos(request):
    return render(request, 'produtos/lista.html')

def detalhe_produto(request, id):
    return HttpResponse(f'Detalhe do produto {id}')
```

## 🔧 Comandos Úteis

### Criar App
```bash
python manage.py startapp nome_do_app
```

### Criar Migrações
```bash
python manage.py makemigrations nome_do_app
```

### Aplicar Migrações
```bash
python manage.py migrate
```

### Verificar Apps Instalados
```bash
python manage.py check
```

### Criar Superusuário (para acessar admin)
```bash
python manage.py createsuperuser
```

## 📝 Checklist ao Criar um Novo App

- [ ] Criar app com `python manage.py startapp`
- [ ] Adicionar ao `INSTALLED_APPS` em `settings.py`
- [ ] Criar arquivo `urls.py` no app
- [ ] Incluir URLs no `urls.py` principal
- [ ] Criar views básicas
- [ ] Criar templates (se necessário)
- [ ] Criar models (se usar banco de dados)
- [ ] Criar migrations (se tiver models)
- [ ] Aplicar migrations

## 🎓 Apps Já Criados no Projeto

### 1. `home` - Página Inicial
- **Localização:** `/root/SinapUm/setup/home/`
- **Função:** Página inicial do servidor
- **URLs:** `/` (raiz)
- **Status:** ✅ Criado e configurado

## 📚 Próximos Passos

Depois de criar um app, você pode:

1. **Criar Models** - Definir estrutura de dados
2. **Criar Views** - Implementar lógica de negócio
3. **Criar Templates** - Criar interfaces HTML
4. **Criar Forms** - Criar formulários
5. **Configurar Admin** - Adicionar ao painel admin

## 🔍 Verificar Apps Instalados

Para ver quais apps estão instalados, verifique:

```bash
cd /root/SinapUm/setup
source ../venv/bin/activate
python manage.py check
```

Ou veja o arquivo `setup/settings.py` na seção `INSTALLED_APPS`.

## ✅ Exemplo Completo

Veja o app `home` já criado como referência:
- `/root/SinapUm/setup/home/` - Estrutura completa
- `/root/SinapUm/setup/home/views.py` - Views de exemplo
- `/root/SinapUm/setup/home/urls.py` - URLs configuradas
- `/root/SinapUm/setup/home/templates/home/` - Templates


