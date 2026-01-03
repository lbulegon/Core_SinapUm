#!/bin/bash
# Script para iniciar o Chatwoot

cd /root/Core_SinapUm

echo "🚀 Iniciando serviços do Chatwoot..."

# Iniciar PostgreSQL e Redis primeiro
echo "📦 Iniciando PostgreSQL e Redis..."
docker compose up -d chatwoot_postgres chatwoot_redis

# Aguardar serviços ficarem prontos
echo "⏳ Aguardando serviços ficarem prontos..."
sleep 10

# Iniciar Rails e Sidekiq
echo "🚀 Iniciando Chatwoot Rails e Sidekiq..."
docker compose up -d chatwoot_rails chatwoot_sidekiq

# Verificar status
echo "✅ Verificando status..."
docker compose ps | grep chatwoot

echo ""
echo "📝 Próximos passos:"
echo "1. Aguarde alguns minutos para o Chatwoot inicializar"
echo "2. Execute as migrações: docker compose exec chatwoot_rails bundle exec rails db:chatwoot_prepare"
echo "3. Acesse: http://seu-ip:3001 ou https://chat.sinapum.com"
echo ""
echo "📋 Ver logs: docker compose logs -f chatwoot_rails"

