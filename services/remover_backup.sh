#!/bin/bash
# Script para remover arquivos de backup do OpenMind

BACKUP_FILE="/root/backup_openmind_remocao_20251214_145016_openmind_ws.tar.gz"

echo "🗑️  Removendo arquivo de backup..."
echo ""

# Verificar se o arquivo existe
if [ ! -f "$BACKUP_FILE" ]; then
    echo "❌ Arquivo não encontrado: $BACKUP_FILE"
    exit 1
fi

# Mostrar informações do arquivo
echo "📋 Informações do arquivo:"
ls -lh "$BACKUP_FILE"
echo ""

# Verificar permissões
echo "🔍 Verificando permissões:"
stat "$BACKUP_FILE" | grep -E "Access|Uid|Gid"
echo ""

# Tentar remover
echo "🗑️  Tentando remover..."
if rm -f "$BACKUP_FILE"; then
    echo "✅ Arquivo removido com sucesso!"
else
    echo "❌ Erro ao remover. Tentando com sudo..."
    if sudo rm -f "$BACKUP_FILE"; then
        echo "✅ Arquivo removido com sudo!"
    else
        echo "❌ Ainda não foi possível remover."
        echo ""
        echo "💡 Tente manualmente:"
        echo "   sudo rm -f $BACKUP_FILE"
        echo "   ou"
        echo "   sudo chmod 644 $BACKUP_FILE && rm -f $BACKUP_FILE"
        exit 1
    fi
fi

echo ""
echo "✅ Operação concluída!"

