#!/bin/bash

# Script para configurar HTTPS no SinapUm
# Uso: ./setup_https.sh [DOMINIO] [EMAIL]

set -e

DOMAIN="${1:-seu-dominio.com}"
EMAIL="${2:-admin@${DOMAIN}}"

echo "╔════════════════════════════════════════════════════════════════╗"
echo "║  🔒 Configuração HTTPS para SinapUm                           ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""
echo "📋 Domínio: ${DOMAIN}"
echo "📧 Email: ${EMAIL}"
echo ""

# Verificar se está no diretório correto
if [ ! -f "docker-compose.yml" ]; then
    echo "❌ Erro: Execute este script no diretório raiz do projeto"
    exit 1
fi

# Verificar se domínio foi fornecido
if [ "$DOMAIN" = "seu-dominio.com" ]; then
    echo "⚠️  AVISO: Usando domínio padrão 'seu-dominio.com'"
    echo "   Para usar seu domínio real, execute:"
    echo "   ./setup_https.sh seu-dominio-real.com seu-email@exemplo.com"
    echo ""
    read -p "Deseja continuar mesmo assim? (s/N): " -n 1 -r
    echo ""
    if [[ ! $REPLY =~ ^[Ss]$ ]]; then
        exit 1
    fi
fi

# Criar diretórios necessários
echo "📁 Criando estrutura de diretórios..."
mkdir -p nginx/conf.d nginx/ssl certbot/conf certbot/www

# Substituir domínio nos arquivos de configuração
echo "🔧 Configurando arquivos..."
sed -i "s/seu-dominio.com/${DOMAIN}/g" nginx/conf.d/sinapum.conf 2>/dev/null || true

# Atualizar ALLOWED_HOSTS no .env se existir
if [ -f ".env" ]; then
    if grep -q "ALLOWED_HOSTS" .env; then
        sed -i "s|ALLOWED_HOSTS=.*|ALLOWED_HOSTS=${DOMAIN},www.${DOMAIN},localhost,127.0.0.1|" .env
    else
        echo "ALLOWED_HOSTS=${DOMAIN},www.${DOMAIN},localhost,127.0.0.1" >> .env
    fi
fi

# Verificar se certificado já existe
if [ -d "certbot/conf/live/${DOMAIN}" ]; then
    echo "✅ Certificado SSL já existe para ${DOMAIN}"
    echo "🚀 Subindo serviços com HTTPS..."
    docker compose -f docker-compose.yml up -d nginx
    echo ""
    echo "✅ HTTPS configurado! Acesse: https://${DOMAIN}"
    exit 0
fi

# Obter certificado inicial
echo "📜 Obtendo certificado SSL do Let's Encrypt..."
echo "   Isso pode levar alguns minutos..."
echo ""

# Primeiro, subir nginx sem SSL para validação
echo "1️⃣  Subindo Nginx temporariamente (sem SSL) para validação..."

# Criar configuração temporária sem SSL
cat > nginx/conf.d/sinapum-temp.conf <<EOF
server {
    listen 80;
    server_name ${DOMAIN} www.${DOMAIN};

    location /.well-known/acme-challenge/ {
        root /var/www/certbot;
    }

    location / {
        proxy_pass http://web:5000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }
}
EOF

# Subir nginx temporário
docker compose up -d nginx || true

# Aguardar nginx estar pronto
echo "   Aguardando Nginx estar pronto..."
sleep 5

# Obter certificado
echo "2️⃣  Solicitando certificado SSL..."
docker run -it --rm \
  -v "$(pwd)/certbot/conf:/etc/letsencrypt" \
  -v "$(pwd)/certbot/www:/var/www/certbot" \
  --network mcp_sinapum_mcp_network \
  certbot/certbot certonly \
  --webroot \
  --webroot-path=/var/www/certbot \
  --email "${EMAIL}" \
  --agree-tos \
  --no-eff-email \
  -d "${DOMAIN}" \
  -d "www.${DOMAIN}" || {
    echo ""
    echo "❌ Erro ao obter certificado SSL"
    echo ""
    echo "Possíveis causas:"
    echo "  - Domínio não está apontando para este servidor"
    echo "  - Porta 80 não está acessível"
    echo "  - Firewall bloqueando conexões"
    echo ""
    echo "Verifique:"
    echo "  1. DNS do domínio aponta para este IP"
    echo "  2. Porta 80 está aberta: sudo ufw allow 80"
    echo "  3. Porta 443 está aberta: sudo ufw allow 443"
    exit 1
  }

# Remover configuração temporária
rm -f nginx/conf.d/sinapum-temp.conf

# Verificar se certificado foi criado
if [ ! -d "certbot/conf/live/${DOMAIN}" ]; then
    echo "❌ Certificado não foi criado. Verifique os logs acima."
    exit 1
fi

echo ""
echo "✅ Certificado SSL obtido com sucesso!"
echo ""

# Atualizar docker-compose para incluir nginx e certbot
echo "3️⃣  Verificando docker-compose.yml..."

# Verificar se nginx já está no docker-compose
if ! grep -q "nginx:" docker-compose.yml; then
    echo "⚠️  Nginx não encontrado no docker-compose.yml"
    echo "   Adicione os serviços nginx e certbot manualmente"
    echo "   Ou use o arquivo docker-compose.https.yml (se existir)"
    echo ""
    read -p "Deseja continuar mesmo assim? (s/N): " -n 1 -r
    echo ""
    if [[ ! $REPLY =~ ^[Ss]$ ]]; then
        exit 1
    fi
fi

# Subir todos os serviços
echo "🚀 Subindo todos os serviços..."
docker compose up -d

echo ""
echo "╔════════════════════════════════════════════════════════════════╗"
echo "║  ✅ HTTPS Configurado com Sucesso!                            ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""
echo "🌐 Acesse seu site em:"
echo "   https://${DOMAIN}"
echo ""
echo "📋 Próximos passos:"
echo "   1. Verificar se o site está acessível via HTTPS"
echo "   2. Testar renovação automática: docker compose exec certbot certbot renew --dry-run"
echo "   3. Verificar logs: docker compose logs nginx"
echo ""
echo "📚 Documentação:"
echo "   - GUIA_HTTPS.md - Guia completo de configuração"
echo "   - DJANGO_HTTPS_EXPLICACAO.md - Explicação sobre Django e HTTPS"
echo ""

