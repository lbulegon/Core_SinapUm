#!/bin/bash
# Script para verificar o status do OpenMind Service

echo "🔍 VERIFICAÇÃO DO OPENMIND SERVICE"
echo "=================================="
echo ""

# 1. Verificar container
echo "1️⃣  Verificando container..."
if docker ps --format '{{.Names}}' | grep -q "^openmind_service$"; then
    echo "   ✅ Container está rodando"
    docker ps --format 'table {{.Names}}\t{{.Status}}\t{{.Ports}}' | grep openmind_service
else
    echo "   ❌ Container não está rodando"
    echo "   Verificando containers parados..."
    docker ps -a | grep openmind_service
fi

echo ""

# 2. Verificar logs
echo "2️⃣  Últimas 30 linhas dos logs:"
echo "--------------------------------"
docker logs --tail 30 openmind_service 2>&1

echo ""
echo ""

# 3. Verificar porta 8001
echo "3️⃣  Verificando porta 8001..."
if sudo lsof -i :8001 > /dev/null 2>&1; then
    echo "   ✅ Porta 8001 está em uso:"
    sudo lsof -i :8001 | head -3
else
    echo "   ⚠️  Porta 8001 não está em uso"
fi

echo ""

# 4. Testar endpoints
echo "4️⃣  Testando endpoints..."
echo ""

# Health check
echo "   Testando /health..."
if curl -f -s http://localhost:8001/health > /dev/null 2>&1; then
    echo "   ✅ /health: OK"
    curl -s http://localhost:8001/health | python3 -m json.tool 2>/dev/null || curl -s http://localhost:8001/health
else
    echo "   ❌ /health: Falhou"
fi

echo ""

# Root
echo "   Testando /..."
if curl -f -s http://localhost:8001/ > /dev/null 2>&1; then
    echo "   ✅ /: OK"
    curl -s http://localhost:8001/ | python3 -m json.tool 2>/dev/null || curl -s http://localhost:8001/
else
    echo "   ❌ /: Falhou"
fi

echo ""
echo ""

# 5. Verificar volumes
echo "5️⃣  Verificando volumes..."
docker inspect openmind_service --format '{{range .Mounts}}{{.Source}} -> {{.Destination}}{{"\n"}}{{end}}' 2>/dev/null | grep -v "^$" || echo "   ⚠️  Não foi possível verificar volumes"

echo ""
echo "✅ Verificação concluída!"

