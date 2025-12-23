#!/bin/bash
# Script para remover pastas antigas do OpenMind APÓS migração bem-sucedida

set -e

echo "🗑️  REMOÇÃO DE PASTAS ANTIGAS DO OPENMIND"
echo "=========================================="
echo ""
echo "⚠️  ATENÇÃO: Este script remove as pastas antigas do OpenMind."
echo "   Certifique-se de que a migração foi concluída e testada!"
echo ""

# Verificar se o novo serviço está rodando
echo "1️⃣  Verificando se o novo serviço está rodando..."
if docker ps --format '{{.Names}}' | grep -q "^openmind_service$"; then
    echo "   ✅ Container openmind_service está rodando"
    
    # Testar health endpoint
    if curl -f http://localhost:8000/health > /dev/null 2>&1; then
        echo "   ✅ Health check passou"
        SERVICE_OK=true
    else
        echo "   ⚠️  Health check falhou, mas container está rodando"
        read -p "   Continuar mesmo assim? (s/N): " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Ss]$ ]]; then
            echo "   ❌ Operação cancelada. Verifique o serviço primeiro."
            exit 1
        fi
        SERVICE_OK=false
    fi
else
    echo "   ❌ Container openmind_service NÃO está rodando!"
    echo "   ⚠️  Certifique-se de que a migração foi concluída antes de remover as pastas antigas."
    read -p "   Continuar mesmo assim? (s/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Ss]$ ]]; then
        echo "   ❌ Operação cancelada."
        exit 1
    fi
    SERVICE_OK=false
fi

echo ""

# Listar pastas a serem removidas
PASTAS=(
    "/root/openmind_ws"
    "/opt/openmind-ai"
)

echo "2️⃣  Pastas que serão removidas:"
for pasta in "${PASTAS[@]}"; do
    if [ -d "$pasta" ]; then
        tamanho=$(du -sh "$pasta" 2>/dev/null | cut -f1)
        echo "   📁 $pasta ($tamanho)"
    else
        echo "   ⚠️  $pasta (não existe)"
    fi
done

echo ""

# Criar backup
echo "3️⃣  Criando backup..."
BACKUP_BASE="/root/backup_openmind_remocao_$(date +%Y%m%d_%H%M%S)"
mkdir -p "$(dirname $BACKUP_BASE)"

for pasta in "${PASTAS[@]}"; do
    if [ -d "$pasta" ]; then
        nome_backup=$(basename "$pasta" | tr '/' '_')
        backup_file="${BACKUP_BASE}_${nome_backup}.tar.gz"
        
        echo "   📦 Fazendo backup de $pasta..."
        tar -czf "$backup_file" -C "$(dirname $pasta)" "$(basename $pasta)" 2>/dev/null || {
            echo "   ⚠️  Erro ao criar backup de $pasta, tentando cópia..."
            cp -r "$pasta" "${BACKUP_BASE}_${nome_backup}" 2>/dev/null || {
                echo "   ❌ Erro ao fazer backup de $pasta"
                read -p "   Continuar mesmo assim? (s/N): " -n 1 -r
                echo
                if [[ ! $REPLY =~ ^[Ss]$ ]]; then
                    echo "   ❌ Operação cancelada"
                    exit 1
                fi
            }
        }
        
        if [ -f "$backup_file" ] || [ -d "${BACKUP_BASE}_${nome_backup}" ]; then
            echo "   ✅ Backup criado"
        fi
    fi
done

echo ""

# Verificar containers relacionados ao openmind_ws
echo "4️⃣  Verificando containers relacionados..."
CONTAINERS_RELACIONADOS=$(docker ps -a --format '{{.Names}}' | grep -E "om1|openmind" | grep -v "openmind_service" || true)

if [ -n "$CONTAINERS_RELACIONADOS" ]; then
    echo "   ⚠️  Containers relacionados encontrados:"
    echo "$CONTAINERS_RELACIONADOS" | while read container; do
        echo "      - $container"
    done
    echo ""
    read -p "   Remover estes containers também? (s/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Ss]$ ]]; then
        echo "$CONTAINERS_RELACIONADOS" | xargs -r docker rm -f
        echo "   ✅ Containers removidos"
    fi
else
    echo "   ✅ Nenhum container relacionado encontrado"
fi

echo ""

# Confirmação final
echo "============================================================"
echo "⚠️  CONFIRMAÇÃO FINAL"
echo "============================================================"
echo ""
echo "📋 Resumo:"
echo "   ✅ Novo serviço: openmind_service (verificado)"
if [ "$SERVICE_OK" = true ]; then
    echo "   ✅ Health check: OK"
else
    echo "   ⚠️  Health check: Não testado ou falhou"
fi
echo "   📦 Backup: Criado em $BACKUP_BASE"
echo ""
echo "🗑️  Pastas que serão REMOVIDAS:"
for pasta in "${PASTAS[@]}"; do
    if [ -d "$pasta" ]; then
        echo "   - $pasta"
    fi
done
echo ""

read -p "🤔 Confirma a remoção? (digite 'CONFIRMAR' para prosseguir): " confirmacao

if [ "$confirmacao" != "CONFIRMAR" ]; then
    echo ""
    echo "❌ Operação cancelada. Nada foi removido."
    echo "📦 Backups criados em: $BACKUP_BASE*"
    exit 0
fi

echo ""
echo "🗑️  Removendo pastas..."

# Remover pastas
for pasta in "${PASTAS[@]}"; do
    if [ -d "$pasta" ]; then
        echo "   Removendo $pasta..."
        rm -rf "$pasta"
        
        if [ ! -d "$pasta" ]; then
            echo "   ✅ $pasta removida"
        else
            echo "   ❌ Erro ao remover $pasta (verifique permissões)"
        fi
    else
        echo "   ⚠️  $pasta não existe, pulando..."
    fi
done

echo ""
echo "✅ Operação concluída!"
echo ""
echo "📦 Backups disponíveis em:"
ls -lh "${BACKUP_BASE}"* 2>/dev/null | awk '{print "   " $9 " (" $5 ")"}' || echo "   (nenhum backup encontrado)"
echo ""
echo "💡 Para restaurar (se necessário):"
echo "   tar -xzf ${BACKUP_BASE}_openmind_ws.tar.gz -C /root/"
echo "   tar -xzf ${BACKUP_BASE}_openmind-ai.tar.gz -C /opt/"

