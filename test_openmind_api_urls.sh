#!/bin/bash
# Script para testar diferentes URLs da API OpenMind.org

API_KEY="om1_live_7d4102a1bf72cc497d7651beb6a98292764b1f77df947c82d086506038ea6b9921efb9d9833045d1"

echo "🔍 Testando diferentes URLs da API OpenMind.org..."
echo ""

URLs=(
    "https://api.openmind.org/v1/chat/completions"
    "https://api.openmind.org/openai/v1/chat/completions"
    "https://api.openmind.org/api/v1/chat/completions"
    "https://openai.openmind.org/v1/chat/completions"
    "https://api.openmind.org/chat/completions"
    "https://api.openmind.org/v1/completions"
    "https://openmind.org/api/v1/chat/completions"
    "https://openmind.org/v1/chat/completions"
)

for url in "${URLs[@]}"; do
    echo "Testando: $url"
    response=$(curl -s -X POST "$url" \
        -H "Authorization: Bearer $API_KEY" \
        -H "Content-Type: application/json" \
        -d '{"model":"gpt-4o","messages":[{"role":"user","content":"test"}]}' \
        -w "\nHTTP_CODE:%{http_code}")
    
    http_code=$(echo "$response" | grep "HTTP_CODE" | cut -d: -f2)
    body=$(echo "$response" | grep -v "HTTP_CODE")
    
    if [ "$http_code" = "200" ]; then
        echo "✅ SUCESSO! URL funcionando: $url"
        echo "Resposta: $body"
        echo ""
        break
    elif [ "$http_code" = "401" ] || [ "$http_code" = "403" ]; then
        echo "⚠️  Erro de autenticação (401/403) - URL pode estar correta mas precisa de autenticação diferente"
        echo "Resposta: $body"
        echo ""
    elif [ "$http_code" = "404" ]; then
        echo "❌ 404 - URL não encontrada"
        echo ""
    else
        echo "⚠️  Status: $http_code"
        echo "Resposta: $body"
        echo ""
    fi
done

echo "✅ Teste concluído!"


