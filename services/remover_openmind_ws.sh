#!/bin/bash
# Script para remover a pasta /root/openmind_ws de forma segura

set -e

SOURCE_DIR="/root/openmind_ws"
BACKUP_DIR="/root/backup_openmind_ws_$(date +%Y%m%d_%H%M%S)"

echo "🗑️  REMOÇÃO DA PASTA /root/openmind_ws"
echo "======================================"
echo ""

# Verificar se a pasta existe
if [ ! -d "$SOURCE_DIR" ]; then
    echo "✅ A pasta $SOURCE_DIR não existe. Nada a fazer."
    exit 0
fi

# Mostrar tamanho da pasta
echo "📊 Informações da pasta:"
du -sh "$SOURCE_DIR" 2>/dev/null || echo "   Não foi possível calcular tamanho"
echo ""

# Listar conteúdo principal
echo "📁 Conteúdo principal:"
ls -lah "$SOURCE_DIR" | head -10
echo ""

# Verificar se há containers Docker rodando relacionados
echo "🔍 Verificando containers Docker relacionados..."
if docker ps -a --format '{{.Names}}' | grep -q -E "om1|openmind"; then
    echo "   ⚠️  Containers relacionados encontrados:"
    docker ps -a --format '{{.Names}}' | grep -E "om1|openmind"
    echo ""
    read -p "   Remover containers também? (s/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Ss]$ ]]; then
        echo "   Removendo containers..."
        docker ps -a --format '{{.Names}}' | grep -E "om1|openmind" | xargs -r docker rm -f
        echo "   ✅ Containers removidos"
    else
        echo "   ⚠️  Containers mantidos. Certifique-se de que não dependem de $SOURCE_DIR"
    fi
else
    echo "   ✅ Nenhum container relacionado encontrado"
fi

echo ""

# Fazer backup antes de remover
echo "💾 Criando backup antes de remover..."
mkdir -p "$(dirname $BACKUP_DIR)"
tar -czf "$BACKUP_DIR.tar.gz" -C "$(dirname $SOURCE_DIR)" "$(basename $SOURCE_DIR)" 2>/dev/null || {
    echo "   ⚠️  Erro ao criar backup completo, tentando cópia simples..."
    cp -r "$SOURCE_DIR" "$BACKUP_DIR" 2>/dev/null || {
        echo "   ❌ Erro ao criar backup. Continuar mesmo assim? (s/N): "
        read -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Ss]$ ]]; then
            echo "   ❌ Operação cancelada"
            exit 1
        fi
    }
}

if [ -f "$BACKUP_DIR.tar.gz" ] || [ -d "$BACKUP_DIR" ]; then
    echo "   ✅ Backup criado em: $BACKUP_DIR"
else
    echo "   ⚠️  Backup não foi criado, mas continuando..."
fi

echo ""

# Confirmação final
echo "⚠️  ATENÇÃO: Esta operação irá REMOVER permanentemente:"
echo "   $SOURCE_DIR"
echo ""
echo "📦 Backup criado em:"
if [ -f "$BACKUP_DIR.tar.gz" ]; then
    echo "   $BACKUP_DIR.tar.gz"
elif [ -d "$BACKUP_DIR" ]; then
    echo "   $BACKUP_DIR"
fi
echo ""

read -p "🤔 Confirma a remoção? (digite 'REMOVER' para confirmar): " confirmacao

if [ "$confirmacao" != "REMOVER" ]; then
    echo ""
    echo "❌ Operação cancelada. Nada foi removido."
    exit 0
fi

echo ""
echo "🗑️  Removendo pasta..."
rm -rf "$SOURCE_DIR"

if [ ! -d "$SOURCE_DIR" ]; then
    echo "✅ Pasta removida com sucesso!"
    echo ""
    echo "📦 Backup disponível em:"
    if [ -f "$BACKUP_DIR.tar.gz" ]; then
        echo "   $BACKUP_DIR.tar.gz"
        echo "   Para restaurar: tar -xzf $BACKUP_DIR.tar.gz -C /root/"
    elif [ -d "$BACKUP_DIR" ]; then
        echo "   $BACKUP_DIR"
        echo "   Para restaurar: mv $BACKUP_DIR $SOURCE_DIR"
    fi
else
    echo "❌ Erro ao remover pasta. Verifique permissões."
    exit 1
fi

echo ""
echo "✅ Operação concluída!"

