# 🚀 Início Rápido - Django na Porta 80

## ⚡ Instalação e Execução Rápida

### 1. Instalar Django e Configurar

```bash
cd /root/SinapUm
./setup_django.sh
```

### 2. Iniciar o Servidor (Desenvolvimento)

```bash
cd /root/SinapUm/setup
source ../venv/bin/activate
sudo python manage.py runserver 0.0.0.0:80
```

### 3. Acessar

- **Página Inicial:** http://69.169.102.84
- **Admin:** http://69.169.102.84/admin

## 🎯 Configuração como Serviço (Produção)

```bash
# Copiar serviço
sudo cp /root/SinapUm/sinapum-django.service /etc/systemd/system/

# Habilitar e iniciar
sudo systemctl daemon-reload
sudo systemctl enable sinapum-django
sudo systemctl start sinapum-django

# Verificar
sudo systemctl status sinapum-django
```

## ✅ Status

Tudo configurado e pronto para uso na **porta 80**!

