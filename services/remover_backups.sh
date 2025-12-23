#!/bin/bash
# Script para remover todos os backups do OpenMind ou backups específicos

echo "🗑️  REMOÇÃO DE BACKUPS DO OPENMIND"
echo "=================================="
echo ""

# Verificar se há backups
BACKUPS=$(ls /root/backup_openmind_remocao_* 2>/dev/null)

if [ -z "$BACKUPS" ]; then
    echo "✅ Nenhum backup encontrado em /root/backup_openmind_remocao_*"
    exit 0
fi

echo "📦 Backups encontrados:"
echo "$BACKUPS" | while read backup; do
    tamanho=$(ls -lh "$backup" | awk '{print $5}')
    echo "   📁 $backup ($tamanho)"
done

echo ""

# Opções
echo "Escolha uma opção:"
echo "1. Remover backup específico"
echo "2. Remover todos os backups"
echo "3. Remover backups mais antigos que X dias"
echo "4. Cancelar"
echo ""
read -p "Opção (1-4): " opcao

case $opcao in
    1)
        echo ""
        echo "Backups disponíveis:"
        echo "$BACKUPS" | nl
        echo ""
        read -p "Número do backup a remover: " num
        backup_escolhido=$(echo "$BACKUPS" | sed -n "${num}p")
        
        if [ -z "$backup_escolhido" ]; then
            echo "❌ Número inválido"
            exit 1
        fi
        
        echo ""
        echo "🗑️  Removendo: $backup_escolhido"
        if rm -f "$backup_escolhido" 2>/dev/null || sudo rm -f "$backup_escolhido"; then
            echo "✅ Backup removido!"
        else
            echo "❌ Erro ao remover. Tente manualmente:"
            echo "   sudo rm -f $backup_escolhido"
        fi
        ;;
    2)
        echo ""
        read -p "⚠️  Confirma remover TODOS os backups? (digite 'CONFIRMAR'): " confirmacao
        if [ "$confirmacao" = "CONFIRMAR" ]; then
            echo "🗑️  Removendo todos os backups..."
            if rm -f /root/backup_openmind_remocao_* 2>/dev/null || sudo rm -f /root/backup_openmind_remocao_*; then
                echo "✅ Todos os backups removidos!"
            else
                echo "❌ Erro ao remover. Tente manualmente:"
                echo "   sudo rm -f /root/backup_openmind_remocao_*"
            fi
        else
            echo "❌ Operação cancelada"
        fi
        ;;
    3)
        echo ""
        read -p "Remover backups mais antigos que quantos dias? " dias
        echo "🗑️  Removendo backups mais antigos que $dias dias..."
        find /root/backup_openmind_remocao_* -type f -mtime +$dias -exec rm -f {} \; 2>/dev/null || \
        find /root/backup_openmind_remocao_* -type f -mtime +$dias -exec sudo rm -f {} \;
        echo "✅ Backups antigos removidos!"
        ;;
    4)
        echo "❌ Operação cancelada"
        exit 0
        ;;
    *)
        echo "❌ Opção inválida"
        exit 1
        ;;
esac

echo ""
echo "✅ Operação concluída!"

