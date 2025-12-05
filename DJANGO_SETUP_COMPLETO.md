# 🚀 Configuração Completa do Django - Porta 80

## ✅ O Que Foi Criado

Projeto Django completo configurado para rodar na **porta 80** como página inicial do servidor.

### Estrutura Criada

```
/root/SinapUm/
├── setup/                          # Projeto Django
│   ├── setup/                      # Configurações do projeto
│   │   ├── settings.py            # ✅ Configurado para servidor
│   │   ├── urls.py                # ✅ URLs configuradas
│   │   ├── wsgi.py                # WSGI para produção
│   │   └── asgi.py                # ASGI para async
│   ├── home/                      # App da página inicial
│   │   ├── views.py               # ✅ Views criadas
│   │   ├── urls.py                # ✅ URLs da app
│   │   ├── templates/home/        # Templates HTML
│   │   │   └── index.html         # ✅ Página inicial linda
│   │   └── static/home/           # Arquivos estáticos
│   ├── manage.py                  # Gerenciador Django
│   └── db.sqlite3                 # Banco de dados
├── venv/                          # Ambiente virtual (será criado)
├── setup_django.sh                # ✅ Script de instalação
├── sinapum-django.service         # ✅ Serviço systemd
└── DJANGO_SETUP_COMPLETO.md       # Este arquivo
```

## 🎯 Configurações Realizadas

### ✅ Settings.py
- `ALLOWED_HOSTS` configurado para aceitar todas as conexões
- Idioma: Português (pt-br)
- Timezone: America/Sao_Paulo
- Arquivos estáticos e mídia configurados
- App `home` adicionado ao INSTALLED_APPS

### ✅ Página Inicial
- Design moderno e responsivo
- Exibe informações do servidor
- Lista serviços disponíveis:
  - OpenMind AI Server (porta 8000)
  - Grafana (porta 3000)
  - Django - Página Inicial (porta 80)

### ✅ Porta 80
- Configurado para rodar na porta 80 (HTTP padrão)
- Pronto para produção com Gunicorn

## 🚀 Instalação Rápida

### Opção 1: Script Automatizado (Recomendado)

```bash
cd /root/SinapUm
chmod +x setup_django.sh
./setup_django.sh
```

### Opção 2: Manual

```bash
cd /root/SinapUm

# Criar ambiente virtual
python3 -m venv venv
source venv/bin/activate

# Instalar dependências
pip install --upgrade pip
pip install Django>=4.2.0 gunicorn whitenoise

# Aplicar migrações
cd setup
python manage.py migrate

# Coletar arquivos estáticos
python manage.py collectstatic --noinput
```

## 🏃 Executar o Servidor

### Desenvolvimento (porta 80)

```bash
cd /root/SinapUm/setup
source ../venv/bin/activate
sudo python manage.py runserver 0.0.0.0:80
```

**⚠️ Nota:** Precisa de `sudo` para usar a porta 80.

### Produção com Gunicorn (porta 80)

```bash
cd /root/SinapUm/setup
source ../venv/bin/activate
sudo gunicorn setup.wsgi:application --bind 0.0.0.0:80 --workers 3
```

### Como Serviço systemd (Recomendado para Produção)

```bash
# Copiar arquivo de serviço
sudo cp /root/SinapUm/sinapum-django.service /etc/systemd/system/

# Recarregar systemd
sudo systemctl daemon-reload

# Habilitar serviço
sudo systemctl enable sinapum-django

# Iniciar serviço
sudo systemctl start sinapum-django

# Verificar status
sudo systemctl status sinapum-django

# Ver logs
sudo journalctl -u sinapum-django -f
```

## 🌐 Acessar

Após iniciar o servidor:

- **Página Inicial:** http://69.169.102.84 ou http://localhost
- **Admin Django:** http://69.169.102.84/admin (criar superusuário primeiro)

## 👤 Criar Superusuário

```bash
cd /root/SinapUm/setup
source ../venv/bin/activate
python manage.py createsuperuser
```

## 📋 Comandos Úteis

```bash
cd /root/SinapUm/setup
source ../venv/bin/activate

# Aplicar migrações
python manage.py migrate

# Coletar arquivos estáticos
python manage.py collectstatic --noinput

# Criar migrações (se criar novos models)
python manage.py makemigrations

# Verificar configuração
python manage.py check --deploy

# Verificar migrações
python manage.py showmigrations
```

## 🔧 Gerenciar Serviço systemd

```bash
# Iniciar
sudo systemctl start sinapum-django

# Parar
sudo systemctl stop sinapum-django

# Reiniciar
sudo systemctl restart sinapum-django

# Status
sudo systemctl status sinapum-django

# Logs em tempo real
sudo journalctl -u sinapum-django -f

# Logs das últimas 100 linhas
sudo journalctl -u sinapum-django -n 100
```

## 🌍 Portas do Servidor

| Serviço | Porta | URL |
|---------|-------|-----|
| Django - Página Inicial | 80 | http://69.169.102.84 |
| OpenMind AI Server | 8000 | http://69.169.102.84:8000 |
| Grafana | 3000 | http://69.169.102.84:3000 |

## 🔒 Firewall

Se tiver firewall ativo, abrir a porta 80:

```bash
sudo ufw allow 80/tcp
sudo ufw reload
```

## 🐛 Troubleshooting

### Erro: "Port 80 already in use"

Verificar o que está usando a porta:

```bash
sudo netstat -tulpn | grep :80
sudo lsof -i :80
```

### Erro: "Permission denied" na porta 80

Precisa usar `sudo` para rodar na porta 80:

```bash
sudo python manage.py runserver 0.0.0.0:80
```

### Django não encontra módulos

Certifique-se de ativar o ambiente virtual:

```bash
source /root/SinapUm/venv/bin/activate
```

### Migrações não aplicadas

```bash
cd /root/SinapUm/setup
source ../venv/bin/activate
python manage.py migrate
```

## ✅ Status Final

- ✅ Projeto Django criado
- ✅ App `home` criada
- ✅ Página inicial HTML moderna
- ✅ Configurado para porta 80
- ✅ Settings ajustados
- ✅ URLs configuradas
- ✅ Serviço systemd criado
- ✅ Script de instalação pronto

## 🎉 Pronto para Usar!

Execute o script de instalação e inicie o servidor:

```bash
cd /root/SinapUm
./setup_django.sh
```

Depois inicie o servidor:

```bash
cd /root/SinapUm/setup
source ../venv/bin/activate
sudo python manage.py runserver 0.0.0.0:80
```

Acesse: **http://69.169.102.84**

