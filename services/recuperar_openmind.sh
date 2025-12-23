#!/bin/bash
# Script para recuperar OpenMind após remoção prematura

echo "🔍 RECUPERAÇÃO DO OPENMIND"
echo "=========================="
echo ""

# 1. Verificar backups
echo "1️⃣  Verificando backups..."
BACKUPS=$(ls /root/backup_openmind_* 2>/dev/null | grep -E "openmind-ai|openmind_ai" | head -1)

if [ -n "$BACKUPS" ]; then
    echo "   ✅ Backup encontrado: $BACKUPS"
    echo ""
    read -p "   Restaurar do backup? (s/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Ss]$ ]]; then
        echo "   📦 Restaurando backup..."
        
        # Extrair para local temporário
        TEMP_DIR="/tmp/openmind_restore_$(date +%Y%m%d_%H%M%S)"
        mkdir -p "$TEMP_DIR"
        
        if [[ "$BACKUPS" == *.tar.gz ]]; then
            tar -xzf "$BACKUPS" -C "$TEMP_DIR"
        else
            cp -r "$BACKUPS"/* "$TEMP_DIR/" 2>/dev/null || cp -r "$BACKUPS" "$TEMP_DIR/"
        fi
        
        # Encontrar a pasta openmind-ai dentro do backup
        SOURCE_DIR=$(find "$TEMP_DIR" -type d -name "openmind-ai" | head -1)
        
        if [ -z "$SOURCE_DIR" ]; then
            # Pode estar na raiz do backup
            if [ -f "$TEMP_DIR/app/main.py" ] || [ -d "$TEMP_DIR/app" ]; then
                SOURCE_DIR="$TEMP_DIR"
            fi
        fi
        
        if [ -n "$SOURCE_DIR" ] && [ -d "$SOURCE_DIR" ]; then
            echo "   ✅ Backup extraído em: $SOURCE_DIR"
            echo ""
            echo "   📋 Conteúdo encontrado:"
            ls -la "$SOURCE_DIR" | head -10
            echo ""
            
            # Continuar com migração
            DEST_DIR="/root/MCP_SinapUm/services/openmind_service"
            echo "   📦 Copiando para: $DEST_DIR"
            
            rsync -av --progress \
                --exclude='venv' \
                --exclude='__pycache__' \
                --exclude='*.pyc' \
                --exclude='.git' \
                "$SOURCE_DIR/" "$DEST_DIR/"
            
            echo "   ✅ Cópia concluída"
            
            # Limpar temporário
            rm -rf "$TEMP_DIR"
        else
            echo "   ❌ Não foi possível encontrar a estrutura da aplicação no backup"
            echo "   📁 Conteúdo do backup:"
            ls -la "$TEMP_DIR"
        fi
    fi
else
    echo "   ❌ Nenhum backup encontrado em /root/backup_openmind_*"
fi

echo ""

# 2. Verificar se está rodando de outro lugar
echo "2️⃣  Verificando processos rodando..."
if pgrep -f "uvicorn.*openmind" > /dev/null; then
    echo "   ⚠️  Processo uvicorn do OpenMind encontrado!"
    echo "   Informações do processo:"
    ps aux | grep "uvicorn.*openmind" | grep -v grep
    echo ""
    echo "   💡 O processo pode estar rodando de outro diretório"
    echo "   Verifique o diretório de trabalho do processo acima"
else
    echo "   ✅ Nenhum processo uvicorn encontrado"
fi

echo ""

# 3. Verificar containers
echo "3️⃣  Verificando containers Docker..."
if docker ps --format '{{.Names}}' | grep -q -E "openmind|om1"; then
    echo "   ⚠️  Containers relacionados encontrados:"
    docker ps --format '{{.Names}}\t{{.Image}}\t{{.Status}}' | grep -E "openmind|om1"
    echo ""
    echo "   💡 Verifique os volumes montados:"
    docker ps --format '{{.Names}}' | grep -E "openmind|om1" | while read container; do
        echo "   Container: $container"
        docker inspect "$container" --format '{{range .Mounts}}{{.Source}} -> {{.Destination}}{{"\n"}}{{end}}' | grep -v "^$"
    done
else
    echo "   ✅ Nenhum container relacionado encontrado"
fi

echo ""

# 4. Verificar porta 8000
echo "4️⃣  Verificando porta 8000..."
if sudo lsof -i :8000 > /dev/null 2>&1; then
    echo "   ⚠️  Porta 8000 está em uso:"
    sudo lsof -i :8000 | head -5
    echo ""
    echo "   💡 Verifique o processo acima para encontrar onde está a aplicação"
else
    echo "   ✅ Porta 8000 não está em uso"
fi

echo ""

# 5. Verificar se há código em outros lugares
echo "5️⃣  Verificando outros locais possíveis..."
LOCAIS_POSSIVEIS=(
    "/root/openmind_ws/OM1"
    "/root/MCP_SinapUm/app_sinapum"
    "/opt"
    "/usr/local/openmind"
)

for local in "${LOCAIS_POSSIVEIS[@]}"; do
    if [ -d "$local" ]; then
        # Procurar por app/main.py ou estrutura FastAPI
        if find "$local" -name "main.py" -path "*/app/*" 2>/dev/null | grep -q .; then
            echo "   ⚠️  Possível localização encontrada: $local"
            find "$local" -name "main.py" -path "*/app/*" 2>/dev/null | head -3
        fi
    fi
done

echo ""
echo "="*60
echo "📋 RESUMO"
echo "="*60
echo ""
echo "Se encontrou backup ou localização:"
echo "1. Execute a migração manualmente copiando os arquivos"
echo "2. Ou use o script migrar_openmind_unificado.sh apontando para o local correto"
echo ""
echo "Se não encontrou nada:"
echo "1. Verifique se há backups em outros locais"
echo "2. Verifique logs do sistema para encontrar onde estava rodando"
echo "3. Pode ser necessário recriar a aplicação do zero"
echo ""

