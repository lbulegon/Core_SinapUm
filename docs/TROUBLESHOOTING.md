# Troubleshooting - OpenMind Service

## 🔍 Verificar Status do Serviço

Execute o script de verificação:

```bash
cd /root/MCP_SinapUm/services/openmind_service
chmod +x verificar_servico.sh
./verificar_servico.sh
```

## ⚠️ Problemas Comuns

### 1. Container não inicia

```bash
# Ver logs detalhados
docker logs openmind_service

# Verificar erros
docker logs openmind_service 2>&1 | grep -i error
```

### 2. Porta 8001 não responde

```bash
# Verificar se o container está rodando
docker ps | grep openmind_service

# Verificar se a porta está mapeada
docker port openmind_service

# Verificar logs
docker logs openmind_service --tail 50
```

### 3. Erro de importação

Se houver erro de importação (ex: `pydantic_settings`):

```bash
# Entrar no container
docker exec -it openmind_service bash

# Verificar instalação
pip list | grep pydantic

# Reinstalar se necessário
pip install pydantic-settings
```

### 4. Erro de permissão

```bash
# Verificar permissões dos volumes
ls -la data/images logs

# Corrigir permissões
chmod -R 755 data logs
```

### 5. Serviço reinicia constantemente

```bash
# Ver logs para identificar o erro
docker logs openmind_service --tail 100

# Verificar health check
docker inspect openmind_service | grep -A 10 Health
```

## 🔧 Soluções Rápidas

### Rebuild completo

```bash
cd /root/MCP_SinapUm/services/openmind_service
docker compose down
docker compose build --no-cache
docker compose up -d
```

### Verificar variáveis de ambiente

```bash
# Verificar .env
cat .env

# Verificar variáveis no container
docker exec openmind_service env | grep OPENMIND
```

### Testar manualmente no container

```bash
# Entrar no container
docker exec -it openmind_service bash

# Testar importação
python3 -c "from app.main import app; print('OK')"

# Testar servidor manualmente
uvicorn app.main:app --host 0.0.0.0 --port 8001
```

## 📋 Checklist de Verificação

- [ ] Arquivo `.env` existe e está configurado
- [ ] Container está rodando: `docker ps | grep openmind_service`
- [ ] Porta 8001 está mapeada: `docker port openmind_service`
- [ ] Logs não mostram erros: `docker logs openmind_service`
- [ ] Diretórios de dados existem: `ls -la data/images logs`
- [ ] Health check responde: `curl http://localhost:8001/health`

