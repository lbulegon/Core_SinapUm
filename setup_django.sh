#!/bin/bash
# Script para configurar o projeto Django na porta 80

set -e

echo "🚀 Configurando projeto Django para porta 80..."

cd /root/SinapUm

# Criar venv se não existir
if [ ! -d "venv" ]; then
    echo "📦 Criando ambiente virtual..."
    python3 -m venv venv
fi

# Ativar venv
echo "🔧 Ativando ambiente virtual..."
source venv/bin/activate

# Instalar/atualizar dependências
echo "📥 Instalando dependências..."
pip install --upgrade pip
if [ -f "requirements.txt" ]; then
    pip install -r requirements.txt
else
    pip install Django>=4.2.0 gunicorn whitenoise cryptography>=41.0.0
fi

# Verificar instalação
echo "✅ Verificando instalação..."
python -c "import django; print(f'Django {django.get_version()} instalado com sucesso!')"

# Aplicar migrações
echo "🔄 Aplicando migrações..."
cd setup
python manage.py migrate

# Coletar arquivos estáticos
echo "📦 Coletando arquivos estáticos..."
python manage.py collectstatic --noinput

echo ""
echo "✅ Django configurado com sucesso!"
echo ""
echo "Para iniciar o servidor na porta 80:"
echo "  cd /root/SinapUm/setup"
echo "  source ../venv/bin/activate"
echo "  sudo python manage.py runserver 0.0.0.0:80"
echo ""
echo "Ou para produção com Gunicorn (porta 80, requer sudo):"
echo "  sudo gunicorn setup.wsgi:application --bind 0.0.0.0:80 --workers 3"
