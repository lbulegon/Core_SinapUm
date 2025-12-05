# 🧪 Como Testar o Servidor OpenMind AI

Guia completo para testar todas as funcionalidades do servidor.

## 📋 Índice

- [Testes Básicos](#-testes-básicos)
- [Testes da API](#-testes-da-api)
- [Teste de Análise de Imagem](#-teste-de-análise-de-imagem)
- [Verificação de Logs](#-verificação-de-logs)
- [Scripts Automatizados](#-scripts-automatizados)
- [Troubleshooting](#-troubleshooting)

---

## ✅ Testes Básicos

### 1. Verificar Status do Serviço

```bash
# No servidor
ssh root@69.169.102.84
systemctl status openmind-ai
```

**Resultado esperado:**
- Status: `active (running)`
- Sem erros no log

### 2. Teste de Conectividade

```bash
# Teste local (no servidor)
curl http://localhost:8000/health

# Teste externo (do seu computador)
curl http://69.169.102.84:8000/health
```

**Resultado esperado:**
```json
{"status": "ok", "version": "1.0.0"}
```
ou similar

### 3. Verificar Documentação Interativa

Abra no navegador:
- **URL**: `http://69.169.102.84:8000/docs`
- **Swagger UI**: Interface interativa para testar todos os endpoints

---

## 🔌 Testes da API

### Teste 1: Health Check

```bash
curl -X GET http://69.169.102.84:8000/health
```

### Teste 2: Root Endpoint

```bash
curl http://69.169.102.84:8000/
```

### Teste 3: Listar Endpoints Disponíveis

```bash
curl http://69.169.102.84:8000/openapi.json | jq '.paths | keys'
```

---

## 🖼️ Teste de Análise de Imagem

### Método 1: Via cURL (linha de comando)

```bash
# Teste básico
curl -X POST "http://69.169.102.84:8000/api/v1/analyze" \
  -H "Content-Type: multipart/form-data" \
  -F "image=@/caminho/para/sua/imagem.jpg"
```

**Exemplo com imagem de teste:**

```bash
# Criar imagem de teste simples
# (ou usar uma imagem que você já tem)

curl -X POST "http://69.169.102.84:8000/api/v1/analyze" \
  -F "image=@produto.jpg"
```

**Resposta esperada:**
```json
{
  "success": true,
  "analysis": {
    "description": "...",
    "category": "...",
    "attributes": {...}
  },
  "processing_time_ms": 1234,
  "request_id": "abc-123-def"
}
```

### Método 2: Via Swagger UI (Recomendado)

1. Acesse: `http://69.169.102.84:8000/docs`
2. Clique em `POST /api/v1/analyze`
3. Clique em "Try it out"
4. Clique em "Choose File" e selecione uma imagem
5. Clique em "Execute"
6. Veja a resposta na interface

### Método 3: Via Python (Script)

```python
import requests

url = "http://69.169.102.84:8000/api/v1/analyze"
files = {"image": open("produto.jpg", "rb")}

response = requests.post(url, files=files)
print(response.json())
```

### Método 4: Via JavaScript/Node.js

```javascript
const FormData = require('form-data');
const fs = require('fs');
const axios = require('axios');

const form = new FormData();
form.append('image', fs.createReadStream('produto.jpg'));

axios.post('http://69.169.102.84:8000/api/v1/analyze', form, {
  headers: form.getHeaders()
})
.then(response => console.log(response.data))
.catch(error => console.error(error));
```

---

## 📊 Verificação de Logs

### 1. Logs do Sistema (systemd)

```bash
# Ver logs em tempo real
ssh root@69.169.102.84 "journalctl -u openmind-ai -f"

# Ver últimas 50 linhas
ssh root@69.169.102.84 "journalctl -u openmind-ai -n 50"

# Ver apenas erros
ssh root@69.169.102.84 "journalctl -u openmind-ai -p err -n 20"
```

### 2. Logs Estruturados (JSON)

```bash
# Logs gerais
ssh root@69.169.102.84 "tail -f /var/log/openmind-ai/app.log"

# Apenas erros
ssh root@69.169.102.84 "tail -f /var/log/openmind-ai/errors.log"

# Requisições HTTP
ssh root@69.169.102.84 "tail -f /var/log/openmind-ai/access.log"

# Análises de imagens
ssh root@69.169.102.84 "tail -f /var/log/openmind-ai/analysis.log"

# Visualizar JSON formatado
ssh root@69.169.102.84 "tail -n 20 /var/log/openmind-ai/app.log | jq ."
```

### 3. Verificar Request ID Específico

```bash
# Buscar por request_id nos logs
ssh root@69.169.102.84 "grep 'request_id_abc123' /var/log/openmind-ai/*.log"
```

---

## 🤖 Scripts Automatizados

### Script PowerShell (Windows)

Execute: `TESTAR_SERVIDOR.ps1`

### Script Bash (Linux/Mac)

Execute: `TESTAR_SERVIDOR.sh`

---

## 🧪 Testes Avançados

### 1. Teste de Rate Limiting

```bash
# Fazer 150 requisições rápidas (limite é 100/min)
for i in {1..150}; do
  curl -s -X GET "http://69.169.102.84:8000/health" &
done
wait

# Verificar logs para ver se rate limit foi aplicado
```

### 2. Teste de Tamanho de Imagem

```bash
# Teste com imagem pequena (< 10MB)
curl -X POST "http://69.169.102.84:8000/api/v1/analyze" \
  -F "image=@imagem_pequena.jpg"

# Teste com imagem grande (> 10MB) - deve falhar
curl -X POST "http://69.169.102.84:8000/api/v1/analyze" \
  -F "image=@imagem_grande.jpg"
```

### 3. Teste de Formatos de Imagem

```bash
# JPEG - deve funcionar
curl -X POST "http://69.169.102.84:8000/api/v1/analyze" \
  -F "image=@produto.jpg"

# PNG - deve funcionar
curl -X POST "http://69.169.102.84:8000/api/v1/analyze" \
  -F "image=@produto.png"

# WEBP - deve funcionar
curl -X POST "http://69.169.102.84:8000/api/v1/analyze" \
  -F "image=@produto.webp"

# GIF - deve falhar (não permitido)
curl -X POST "http://69.169.102.84:8000/api/v1/analyze" \
  -F "image=@animacao.gif"
```

### 4. Teste de Resposta a Erros

```bash
# Enviar sem arquivo - deve retornar erro
curl -X POST "http://69.169.102.84:8000/api/v1/analyze"

# Enviar arquivo não-imagem - deve retornar erro
curl -X POST "http://69.169.102.84:8000/api/v1/analyze" \
  -F "image=@documento.pdf"
```

---

## 🔍 Verificação de Performance

### 1. Tempo de Resposta

```bash
# Medir tempo de resposta
time curl -X POST "http://69.169.102.84:8000/api/v1/analyze" \
  -F "image=@produto.jpg"
```

### 2. Múltiplas Requisições Sequenciais

```bash
# Testar 10 requisições sequenciais
for i in {1..10}; do
  echo "Requisição $i:"
  time curl -s -X POST "http://69.169.102.84:8000/api/v1/analyze" \
    -F "image=@produto.jpg" | jq '.processing_time_ms'
done
```

### 3. Uso de Recursos

```bash
# No servidor, verificar uso de CPU e memória
ssh root@69.169.102.84 "top -p \$(pgrep -f 'uvicorn.*openmind')"

# Ou usar htop
ssh root@69.169.102.84 "htop -p \$(pgrep -f 'uvicorn.*openmind')"
```

---

## ⚠️ Troubleshooting

### Problema: Serviço não responde

```bash
# Verificar se está rodando
systemctl status openmind-ai

# Ver logs de erro
journalctl -u openmind-ai -n 50 -p err

# Reiniciar serviço
systemctl restart openmind-ai
```

### Problema: Erro 500 na API

```bash
# Verificar logs
journalctl -u openmind-ai -n 100 | grep -i error

# Verificar logs estruturados
tail -n 50 /var/log/openmind-ai/errors.log | jq .
```

### Problema: Timeout nas requisições

```bash
# Verificar conexão com API OpenMind
curl -H "Authorization: Bearer $OPENMIND_ORG_API_KEY" \
  https://api.openmind.org/api/core/openai/v1/models

# Verificar timeout no .env
ssh root@69.169.102.84 "grep TIMEOUT /opt/openmind-ai/.env"
```

### Problema: Imagem não processada

```bash
# Verificar tamanho da imagem
ls -lh imagem.jpg

# Verificar formato
file imagem.jpg

# Verificar logs de análise
tail -f /var/log/openmind-ai/analysis.log
```

---

## ✅ Checklist de Testes

Use este checklist para validar que tudo está funcionando:

- [ ] Serviço está rodando (`systemctl status`)
- [ ] Health endpoint responde (`/health`)
- [ ] Documentação está acessível (`/docs`)
- [ ] API aceita requisições de imagem
- [ ] Análise de imagem retorna resultado válido
- [ ] Logs estão sendo gerados corretamente
- [ ] Request ID está presente nas respostas
- [ ] Rate limiting funciona (se configurado)
- [ ] Validação de tamanho de imagem funciona
- [ ] Validação de formato de imagem funciona
- [ ] Erros são logados corretamente
- [ ] Logs JSON estão no formato correto

---

## 📞 Próximos Passos

Após validar os testes básicos:

1. **Configurar monitoramento** - Grafana/Loki
2. **Configurar alertas** - Para erros e downtime
3. **Otimizar performance** - Baseado nos testes
4. **Configurar backup** - Dos logs e configurações

---

**Última atualização**: Janeiro 2024

