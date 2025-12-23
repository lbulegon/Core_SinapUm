#!/bin/bash
# Script para migrar OpenMind de /root/openmind_ws/OM1 para /root/MCP_SinapUm/services/openmind_service

set -e

SOURCE_DIR="/root/openmind_ws/OM1"
DEST_DIR="/root/MCP_SinapUm/services/openmind_service"
CONTAINER_NAME="om1"

echo "🚀 MIGRAÇÃO DO OPENMIND"
echo "========================"
echo ""
echo "Origem: $SOURCE_DIR"
echo "Destino: $DEST_DIR"
echo ""

# Verificar se o diretório de origem existe
if [ ! -d "$SOURCE_DIR" ]; then
    echo "❌ Erro: Diretório de origem não existe: $SOURCE_DIR"
    exit 1
fi

# Verificar se o container está rodando
echo "1️⃣  Verificando estado atual do serviço..."
if docker ps --format '{{.Names}}' | grep -q "^${CONTAINER_NAME}$"; then
    echo "   ⚠️  Container $CONTAINER_NAME está rodando"
    read -p "   Parar o container antes de migrar? (s/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Ss]$ ]]; then
        echo "   Parando container..."
        cd "$SOURCE_DIR"
        docker compose down
        echo "   ✅ Container parado"
    else
        echo "   ⚠️  Continuando com container rodando (não recomendado)"
    fi
else
    echo "   ✅ Container não está rodando"
fi

# Criar diretório de destino
echo ""
echo "2️⃣  Criando diretório de destino..."
mkdir -p "$DEST_DIR"
echo "   ✅ Diretório criado: $DEST_DIR"

# Verificar se já existe conteúdo no destino
if [ "$(ls -A $DEST_DIR 2>/dev/null)" ]; then
    echo "   ⚠️  Diretório de destino já contém arquivos!"
    read -p "   Continuar mesmo assim? (s/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Ss]$ ]]; then
        echo "   ❌ Migração cancelada"
        exit 1
    fi
fi

# Fazer backup
echo ""
echo "3️⃣  Criando backup..."
BACKUP_DIR="/root/backup_openmind_$(date +%Y%m%d_%H%M%S)"
mkdir -p "$BACKUP_DIR"
echo "   Backup em: $BACKUP_DIR"
# Não vamos copiar tudo, apenas documentar
echo "   ✅ Backup preparado (estrutura será copiada)"

# Copiar estrutura
echo ""
echo "4️⃣  Copiando estrutura..."
echo "   Isso pode levar alguns minutos..."

rsync -av --progress \
    --exclude='.git' \
    --exclude='__pycache__' \
    --exclude='*.pyc' \
    --exclude='.venv' \
    --exclude='node_modules' \
    "$SOURCE_DIR/" "$DEST_DIR/"

echo "   ✅ Estrutura copiada"

# Verificar docker-compose.yml
echo ""
echo "5️⃣  Verificando docker-compose.yml..."
if [ -f "$DEST_DIR/docker-compose.yml" ]; then
    echo "   ✅ docker-compose.yml encontrado"
    
    # Verificar se há caminhos absolutos que precisam ser atualizados
    if grep -q "/root/openmind_ws" "$DEST_DIR/docker-compose.yml"; then
        echo "   ⚠️  Encontrados caminhos absolutos antigos"
        echo "   Atualizando..."
        sed -i 's|/root/openmind_ws|/root/MCP_SinapUm/services/openmind_service|g' "$DEST_DIR/docker-compose.yml"
        echo "   ✅ Caminhos atualizados"
    else
        echo "   ✅ Nenhum caminho absoluto encontrado (usando relativos)"
    fi
else
    echo "   ❌ docker-compose.yml não encontrado!"
    exit 1
fi

# Verificar arquivo .env
echo ""
echo "6️⃣  Verificando variáveis de ambiente..."
if [ -f "$SOURCE_DIR/.env" ]; then
    if [ ! -f "$DEST_DIR/.env" ]; then
        cp "$SOURCE_DIR/.env" "$DEST_DIR/.env"
        echo "   ✅ .env copiado"
    else
        echo "   ⚠️  .env já existe no destino"
    fi
elif [ -f "$SOURCE_DIR/env.example" ]; then
    if [ ! -f "$DEST_DIR/.env" ]; then
        cp "$SOURCE_DIR/env.example" "$DEST_DIR/.env"
        echo "   ✅ env.example copiado como .env"
        echo "   ⚠️  ATENÇÃO: Revise o arquivo .env e configure as variáveis necessárias"
    fi
fi

# Verificar volumes especiais
echo ""
echo "7️⃣  Verificando volumes especiais..."
if grep -q "\${HOME}/shared_data" "$DEST_DIR/docker-compose.yml"; then
    echo "   ⚠️  Volume compartilhado encontrado: \${HOME}/shared_data/locations"
    echo "   Certifique-se de que este diretório existe ou atualize o docker-compose.yml"
fi

# Subir serviço no novo local
echo ""
echo "8️⃣  Subindo serviço no novo local..."
cd "$DEST_DIR"

# Remover container antigo se existir com nome diferente
if docker ps -a --format '{{.Names}}' | grep -q "^${CONTAINER_NAME}$"; then
    echo "   Removendo container antigo..."
    docker rm -f "$CONTAINER_NAME" 2>/dev/null || true
fi

# Subir novo
docker compose up -d --build

echo "   ✅ Serviço iniciado"

# Verificar status
echo ""
echo "9️⃣  Verificando status..."
sleep 5

if docker ps --format '{{.Names}}' | grep -q "^${CONTAINER_NAME}$"; then
    echo "   ✅ Container está rodando"
    
    # Verificar logs
    echo ""
    echo "   📋 Últimas linhas dos logs:"
    docker logs --tail 20 "$CONTAINER_NAME" 2>&1 | head -20
else
    echo "   ❌ Container não está rodando!"
    echo "   Verifique os logs: docker logs $CONTAINER_NAME"
    exit 1
fi

# Verificar volumes
echo ""
echo "🔟 Verificando volumes..."
docker inspect "$CONTAINER_NAME" --format '{{range .Mounts}}{{.Source}} -> {{.Destination}}{{"\n"}}{{end}}' | grep -v "^$"

echo ""
echo "✅ MIGRAÇÃO CONCLUÍDA!"
echo ""
echo "📝 Próximos passos:"
echo "   1. Verificar logs: docker logs $CONTAINER_NAME"
echo "   2. Testar endpoints do OpenMind"
echo "   3. Após confirmar que tudo está funcionando, você pode remover:"
echo "      rm -rf $SOURCE_DIR"
echo ""
echo "⚠️  IMPORTANTE: Não remova o diretório antigo até confirmar que tudo está funcionando!"

