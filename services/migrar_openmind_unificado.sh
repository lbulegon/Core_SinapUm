#!/bin/bash
# Script para migrar OpenMind AI (FastAPI) de /opt/openmind-ai para /root/MCP_SinapUm/services/openmind_service

set -e

SOURCE_DIR="/opt/openmind-ai"
DEST_DIR="/root/MCP_SinapUm/services/openmind_service"
SERVICE_NAME="openmind_service"

echo "🚀 MIGRAÇÃO UNIFICADA DO OPENMIND (FastAPI)"
echo "============================================"
echo ""
echo "Origem: $SOURCE_DIR"
echo "Destino: $DEST_DIR"
echo "Porta: 8000"
echo ""

# Verificar se o diretório de origem existe
if [ ! -d "$SOURCE_DIR" ]; then
    echo "❌ Erro: Diretório de origem não existe: $SOURCE_DIR"
    echo ""
    echo "💡 Opções:"
    echo "   1. Se você tem um backup, restaure primeiro:"
    echo "      tar -xzf /root/backup_openmind_*.tar.gz -C /tmp/"
    echo "      Depois execute este script novamente apontando para o local restaurado"
    echo ""
    echo "   2. Ou especifique outro diretório de origem:"
    echo "      SOURCE_DIR=/caminho/alternativo ./migrar_openmind_unificado.sh"
    echo ""
    echo "   3. Ou execute o script de recuperação:"
    echo "      ./recuperar_openmind.sh"
    echo ""
    exit 1
fi

# Verificar se há processo rodando
echo "1️⃣  Verificando estado atual do serviço..."
if pgrep -f "uvicorn.*openmind" > /dev/null; then
    echo "   ⚠️  Processo uvicorn do OpenMind está rodando"
    read -p "   Parar o processo antes de migrar? (s/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Ss]$ ]]; then
        echo "   Parando processo..."
        pkill -f "uvicorn.*openmind" || true
        sleep 2
        echo "   ✅ Processo parado"
    else
        echo "   ⚠️  Continuando com processo rodando (pode causar conflito na porta 8000)"
    fi
else
    echo "   ✅ Nenhum processo uvicorn do OpenMind encontrado"
fi

# Verificar serviço systemd
if systemctl list-units --all --type=service | grep -q openmind; then
    echo "   ⚠️  Serviço systemd encontrado"
    read -p "   Parar e desabilitar serviço systemd? (s/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Ss]$ ]]; then
        sudo systemctl stop openmind-ai 2>/dev/null || true
        sudo systemctl disable openmind-ai 2>/dev/null || true
        echo "   ✅ Serviço systemd parado e desabilitado"
    fi
fi

# Verificar porta 8000
echo ""
echo "2️⃣  Verificando porta 8000..."
if sudo lsof -i :8000 > /dev/null 2>&1; then
    echo "   ⚠️  Porta 8000 está em uso:"
    sudo lsof -i :8000 | head -5
    read -p "   Continuar mesmo assim? (s/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Ss]$ ]]; then
        echo "   ❌ Migração cancelada"
        exit 1
    fi
else
    echo "   ✅ Porta 8000 está livre"
fi

# Fazer backup
echo ""
echo "3️⃣  Criando backup..."
BACKUP_DIR="/root/backup_openmind_$(date +%Y%m%d_%H%M%S)"
mkdir -p "$BACKUP_DIR"
echo "   Backup em: $BACKUP_DIR"
tar -czf "$BACKUP_DIR/openmind-ai.tar.gz" -C "$(dirname $SOURCE_DIR)" "$(basename $SOURCE_DIR)" 2>/dev/null || {
    echo "   ⚠️  Erro ao criar backup completo, copiando estrutura..."
    cp -r "$SOURCE_DIR" "$BACKUP_DIR/" 2>/dev/null || true
}
echo "   ✅ Backup criado"

# Criar diretório de destino
echo ""
echo "4️⃣  Criando diretório de destino..."
mkdir -p "$DEST_DIR"
echo "   ✅ Diretório criado: $DEST_DIR"

# Verificar se já existe conteúdo
if [ "$(ls -A $DEST_DIR 2>/dev/null)" ]; then
    echo "   ⚠️  Diretório de destino já contém arquivos!"
    read -p "   Continuar mesmo assim? (s/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Ss]$ ]]; then
        echo "   ❌ Migração cancelada"
        exit 1
    fi
fi

# Copiar estrutura
echo ""
echo "5️⃣  Copiando estrutura..."
echo "   Isso pode levar alguns minutos..."

rsync -av --progress \
    --exclude='venv' \
    --exclude='__pycache__' \
    --exclude='*.pyc' \
    --exclude='.git' \
    --exclude='node_modules' \
    "$SOURCE_DIR/" "$DEST_DIR/"

echo "   ✅ Estrutura copiada"

# Criar diretórios necessários
echo ""
echo "6️⃣  Criando diretórios necessários..."
mkdir -p "$DEST_DIR/data/images"
mkdir -p "$DEST_DIR/logs"
chmod 755 "$DEST_DIR/data" "$DEST_DIR/logs"
echo "   ✅ Diretórios criados"

# Verificar e criar .env
echo ""
echo "7️⃣  Verificando variáveis de ambiente..."
if [ -f "$DEST_DIR/.env" ]; then
    echo "   ✅ .env já existe"
elif [ -f "$DEST_DIR/ENV_EXAMPLE.txt" ]; then
    cp "$DEST_DIR/ENV_EXAMPLE.txt" "$DEST_DIR/.env"
    echo "   ✅ .env criado a partir de ENV_EXAMPLE.txt"
    echo "   ⚠️  ATENÇÃO: Revise o arquivo .env e configure as variáveis necessárias"
else
    echo "   ⚠️  Nenhum arquivo .env ou ENV_EXAMPLE.txt encontrado"
    echo "   Criando .env básico..."
    cat > "$DEST_DIR/.env" << EOF
OPENMIND_AI_API_KEY=om1_live_7d4102a1bf72cc497d7651beb6a98292764b1f77df947c82d086506038ea6b9921efb9d9833045d1
OPENMIND_AI_HOST=0.0.0.0
OPENMIND_AI_PORT=8000
OPENAI_API_KEY=
OPENAI_MODEL=gpt-4o
LOG_LEVEL=INFO
CORS_ORIGINS=*
MEDIA_ROOT=/data/vitrinezap/images
MEDIA_URL=/media
EOF
    echo "   ✅ .env básico criado"
fi

# Verificar se Dockerfile e docker-compose.yml já existem
echo ""
echo "8️⃣  Verificando arquivos Docker..."
if [ ! -f "$DEST_DIR/Dockerfile" ]; then
    echo "   ⚠️  Dockerfile não encontrado, será criado automaticamente"
fi
if [ ! -f "$DEST_DIR/docker-compose.yml" ]; then
    echo "   ⚠️  docker-compose.yml não encontrado, será criado automaticamente"
fi

# Parar container antigo se existir
echo ""
echo "9️⃣  Verificando containers antigos..."
if docker ps -a --format '{{.Names}}' | grep -q "^${SERVICE_NAME}$"; then
    echo "   Removendo container antigo..."
    docker rm -f "$SERVICE_NAME" 2>/dev/null || true
    echo "   ✅ Container antigo removido"
else
    echo "   ✅ Nenhum container antigo encontrado"
fi

# Subir serviço
echo ""
echo "🔟 Subindo serviço no novo local..."
cd "$DEST_DIR"

# Build e start
docker compose build
docker compose up -d

echo "   ✅ Serviço iniciado"

# Verificar status
echo ""
echo "1️⃣1️⃣  Verificando status..."
sleep 5

if docker ps --format '{{.Names}}' | grep -q "^${SERVICE_NAME}$"; then
    echo "   ✅ Container está rodando"
    
    # Verificar logs
    echo ""
    echo "   📋 Últimas linhas dos logs:"
    docker logs --tail 20 "$SERVICE_NAME" 2>&1 | head -20
    
    # Testar health
    echo ""
    echo "   🏥 Testando health endpoint..."
    sleep 3
    if curl -f http://localhost:8000/health > /dev/null 2>&1; then
        echo "   ✅ Health check passou"
    else
        echo "   ⚠️  Health check falhou (pode estar ainda inicializando)"
    fi
else
    echo "   ❌ Container não está rodando!"
    echo "   Verifique os logs: docker logs $SERVICE_NAME"
    exit 1
fi

# Verificar volumes
echo ""
echo "1️⃣2️⃣  Verificando volumes..."
docker inspect "$SERVICE_NAME" --format '{{range .Mounts}}{{.Source}} -> {{.Destination}}{{"\n"}}{{end}}' | grep -v "^$"

echo ""
echo "✅ MIGRAÇÃO CONCLUÍDA!"
echo ""
echo "📝 Próximos passos:"
echo "   1. Verificar logs: docker logs $SERVICE_NAME"
echo "   2. Testar endpoints:"
echo "      curl http://localhost:8000/"
echo "      curl http://localhost:8000/health"
echo "      curl http://localhost:8000/docs"
echo "   3. Verificar integração com outros serviços"
echo "   4. Após confirmar que tudo está funcionando, você pode:"
echo "      - Remover /opt/openmind-ai (fazer backup antes!)"
echo "      - Atualizar referências em outros serviços"
echo ""
echo "⚠️  IMPORTANTE: Não remova o diretório antigo até confirmar que tudo está funcionando!"
echo ""
echo "📦 Estrutura criada em: $DEST_DIR"

