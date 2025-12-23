# Verificação do OpenMind Unificado

## 🔍 Como Verificar Manualmente

Execute os seguintes comandos para verificar se o OpenMind está unificado e funcionando:

### 1. Verificar Containers Docker

```bash
# Ver container novo (deve estar rodando)
docker ps | grep openmind_service

# Ver containers antigos (não devem estar rodando)
docker ps -a | grep -E "om1|openmind" | grep -v "openmind_service"
```

**Resultado esperado:**
- ✅ `openmind_service` deve estar rodando
- ✅ Nenhum container `om1` deve estar rodando

### 2. Verificar Porta 8000

```bash
# Ver o que está usando a porta 8000
sudo lsof -i :8000
# ou
netstat -tulpn | grep 8000
```

**Resultado esperado:**
- ✅ Porta 8000 deve estar em uso pelo container `openmind_service`

### 3. Verificar Pastas

```bash
# Verificar se pastas antigas foram removidas
ls -la /root/openmind_ws 2>&1
ls -la /opt/openmind-ai 2>&1

# Verificar se pasta nova existe
ls -la /root/MCP_SinapUm/services/openmind_service
```

**Resultado esperado:**
- ✅ `/root/openmind_ws` não deve existir (ou estar vazia)
- ✅ `/opt/openmind-ai` não deve existir (ou estar vazia)
- ✅ `/root/MCP_SinapUm/services/openmind_service` deve existir

### 4. Verificar Endpoints HTTP

```bash
# Health check
curl http://localhost:8000/health

# Root
curl http://localhost:8000/

# Documentação
curl http://localhost:8000/docs
```

**Resultado esperado:**
- ✅ Todos os endpoints devem responder com status 200

### 5. Verificar Estrutura do Serviço

```bash
cd /root/MCP_SinapUm/services/openmind_service
ls -la

# Verificar arquivos importantes
ls -la docker-compose.yml Dockerfile app/main.py requirements.txt
```

**Resultado esperado:**
- ✅ Todos os arquivos devem existir

### 6. Verificar Logs

```bash
docker logs openmind_service --tail 20
```

**Resultado esperado:**
- ✅ Logs devem mostrar que o servidor está rodando
- ✅ Sem erros críticos

## ✅ Checklist de Unificação

- [ ] Container `openmind_service` está rodando
- [ ] Container `om1` NÃO está rodando
- [ ] Porta 8000 está em uso pelo `openmind_service`
- [ ] Pasta `/root/openmind_ws` foi removida ou não existe
- [ ] Pasta `/opt/openmind-ai` foi removida ou não existe
- [ ] Pasta `/root/MCP_SinapUm/services/openmind_service` existe
- [ ] Endpoint `/health` responde corretamente
- [ ] Endpoint `/docs` está acessível
- [ ] Arquivos Docker (docker-compose.yml, Dockerfile) existem
- [ ] Aplicação FastAPI (app/main.py) existe

## 🎯 Status Esperado

### ✅ Unificação Completa

Se tudo estiver correto, você deve ter:

1. **Apenas UM serviço OpenMind** rodando:
   - Container: `openmind_service`
   - Porta: `8000`
   - Tecnologia: FastAPI

2. **Pastas antigas removidas**:
   - `/root/openmind_ws` ❌ (removida)
   - `/opt/openmind-ai` ❌ (removida)

3. **Pasta nova funcionando**:
   - `/root/MCP_SinapUm/services/openmind_service` ✅

4. **Endpoints funcionando**:
   - `http://localhost:8000/` ✅
   - `http://localhost:8000/health` ✅
   - `http://localhost:8000/docs` ✅

## 🔧 Script de Verificação Automatizada

Execute o script Python para verificação completa:

```bash
cd /root/MCP_SinapUm/services
python3 verificar_openmind_unificado.py
```

O script verificará todos os pontos acima automaticamente.

## 🆘 Problemas Comuns

### Container não está rodando

```bash
cd /root/MCP_SinapUm/services/openmind_service
docker compose up -d
```

### Porta 8000 em uso por outro processo

```bash
# Ver o que está usando
sudo lsof -i :8000

# Parar processo antigo se necessário
sudo kill <PID>
```

### Pastas antigas ainda existem

```bash
# Verificar se podem ser removidas
cd /root/MCP_SinapUm/services
./remover_pastas_antigas.sh
```

