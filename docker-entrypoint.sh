#!/bin/bash
set -e

# Aguardar PostgreSQL estar pronto
if [ "$1" = "gunicorn" ]; then
    echo "Aguardando PostgreSQL..."
    until PGPASSWORD=$POSTGRES_PASSWORD psql -h "$POSTGRES_HOST" -U "$POSTGRES_USER" -d "$POSTGRES_DB" -c '\q' 2>/dev/null; do
        >&2 echo "PostgreSQL não está disponível - aguardando..."
        sleep 1
    done
    echo "PostgreSQL está pronto!"
fi

# Executar migrações
echo "Executando migrações..."
python manage.py migrate --noinput

# Seed MCP Registry (vitrinezap.analisar_produto + ClientApp)
echo "Executando seed do MCP Registry..."
python manage.py seed_mcp_registry 2>/dev/null || true

# Coletar arquivos estáticos
echo "Coletando arquivos estáticos..."
python manage.py collectstatic --noinput --clear || true

# Criar superusuário se não existir (apenas em desenvolvimento)
if [ "$DEBUG" = "True" ] && [ "$CREATE_SUPERUSER" = "True" ]; then
    echo "Criando superusuário..."
    python manage.py shell << EOF
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@example.com', 'admin123')
    print('Superusuário criado: admin/admin123')
else:
    print('Superusuário já existe')
EOF
fi

# Executar comando passado
exec "$@"

