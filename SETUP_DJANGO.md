# Setup do Projeto Django - Página Inicial do Servidor

## 🎯 Objetivo

Configurar o projeto Django existente em `/root/SinapUm/setup` para servir como página inicial do servidor na porta 80.

## 📋 Situação Atual

- ✅ Projeto Django existe em `/root/SinapUm/setup`
- ❌ Django não está instalado
- ❌ Migrações não aplicadas (18 pendentes)
- ⚠️ Porta 8000 está em uso pelo OpenMind AI Server

## 🚀 Passo a Passo

### 1. Criar Ambiente Virtual

```bash
cd /root/SinapUm
python3 -m venv venv
source venv/bin/activate
```

### 2. Instalar Django e Dependências

```bash
pip install --upgrade pip
pip install Django>=4.2.0
pip install gunicorn
pip install whitenoise
```

### 3. Aplicar Migrações

```bash
cd /root/SinapUm/setup
python manage.py migrate
```

### 4. Criar Superusuário (opcional)

```bash
python manage.py createsuperuser
```

### 5. Rodar Servidor de Desenvolvimento (Porta 80)

**IMPORTANTE**: Para rodar na porta 80, precisa ser root ou usar sudo.

```bash
# Rodar na porta 80 (requer root/sudo)
sudo python manage.py runserver 0.0.0.0:80

# Ou rodar em outra porta (ex: 3000)
python manage.py runserver 0.0.0.0:3000
```

### 6. Configurar para Produção com Gunicorn

```bash
# Na porta 80 (requer root)
sudo gunicorn setup.wsgi:application --bind 0.0.0.0:80 --workers 3

# Na porta 3000
gunicorn setup.wsgi:application --bind 0.0.0.0:3000 --workers 3
```

## ⚙️ Configurações Necessárias

### Ajustar ALLOWED_HOSTS

Editar `/root/SinapUm/setup/setup/settings.py`:

```python
ALLOWED_HOSTS = [
    'localhost',
    '127.0.0.1',
    '69.169.102.84',
    '*',  # Para desenvolvimento
]
```

### Configurar Arquivos Estáticos

Adicionar ao `settings.py`:

```python
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'
```

## 🔧 Script Automatizado

Criar script `setup_django.sh`:

```bash
#!/bin/bash
cd /root/SinapUm

# Criar venv se não existir
if [ ! -d "venv" ]; then
    python3 -m venv venv
fi

# Ativar venv
source venv/bin/activate

# Instalar dependências
pip install --upgrade pip
pip install Django gunicorn whitenoise

# Aplicar migrações
cd setup
python manage.py migrate

echo "✅ Django configurado com sucesso!"
echo "Para iniciar o servidor:"
echo "  cd /root/SinapUm/setup"
echo "  source ../venv/bin/activate"
echo "  python manage.py runserver 0.0.0.0:3000"
```

## 📝 Próximos Passos

1. ✅ Criar app `home` para a página inicial
2. ✅ Criar templates HTML
3. ✅ Configurar URLs
4. ✅ Criar views
5. ✅ Configurar serviço systemd para produção

## 🔍 Verificar Status

```bash
# Ver se Django está instalado
python -c "import django; print(django.get_version())"

# Ver migrações pendentes
cd /root/SinapUm/setup
python manage.py showmigrations

# Verificar porta 80
sudo netstat -tulpn | grep :80
```

## ⚠️ Notas Importantes

- **Porta 80**: Requer privilégios root/sudo
- **Porta 3000**: Pode rodar como usuário normal
- **Firewall**: Verificar se a porta está aberta
- **Produção**: Usar Gunicorn + Nginx recomendado

