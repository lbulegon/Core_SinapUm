# Remover Pastas Antigas do OpenMind

## ⚠️ IMPORTANTE

**Só execute a remoção APÓS confirmar que:**
1. ✅ A migração foi concluída com sucesso
2. ✅ O novo serviço `openmind_service` está rodando
3. ✅ Todos os endpoints estão funcionando
4. ✅ A integração com outros serviços foi testada

## 🚀 Como Remover

### Opção 1: Script Automatizado (Recomendado)

```bash
cd /root/MCP_SinapUm/services
chmod +x remover_pastas_antigas.sh
./remover_pastas_antigas.sh
```

O script irá:
1. ✅ Verificar se o novo serviço está rodando
2. ✅ Testar health check
3. ✅ Fazer backup das pastas antigas
4. ✅ Verificar containers relacionados
5. ✅ Pedir confirmação final
6. ✅ Remover as pastas

### Opção 2: Remoção Manual

#### Remover `/root/openmind_ws`

```bash
# 1. Fazer backup
tar -czf /root/backup_openmind_ws_$(date +%Y%m%d).tar.gz /root/openmind_ws

# 2. Verificar containers relacionados
docker ps -a | grep -E "om1|openmind"

# 3. Remover containers se necessário
docker rm -f <container_name>

# 4. Remover pasta
rm -rf /root/openmind_ws
```

#### Remover `/opt/openmind-ai`

```bash
# 1. Fazer backup
tar -czf /root/backup_openmind_ai_$(date +%Y%m%d).tar.gz /opt/openmind-ai

# 2. Verificar processos
ps aux | grep uvicorn

# 3. Parar processo se estiver rodando
pkill -f "uvicorn.*openmind"

# 4. Verificar serviço systemd
systemctl status openmind-ai  # Se existir

# 5. Remover pasta
sudo rm -rf /opt/openmind-ai
```

## 📋 Checklist Antes de Remover

- [ ] Novo serviço `openmind_service` está rodando
- [ ] Health check: `curl http://localhost:8000/health` retorna OK
- [ ] Documentação: `curl http://localhost:8000/docs` funciona
- [ ] Endpoint de análise testado
- [ ] Integração com outros serviços testada
- [ ] Backup criado das pastas antigas
- [ ] Containers antigos removidos (se houver)
- [ ] Processos antigos parados (se houver)

## 🔄 Restaurar (Se Necessário)

Se precisar restaurar as pastas:

```bash
# Restaurar /root/openmind_ws
tar -xzf /root/backup_openmind_ws_YYYYMMDD.tar.gz -C /root/

# Restaurar /opt/openmind-ai
tar -xzf /root/backup_openmind_ai_YYYYMMDD.tar.gz -C /opt/
```

## 📦 Pastas que Serão Removidas

1. **`/root/openmind_ws/`**
   - OpenMind OM1 (Docker + ROS2)
   - Não é mais necessário (unificamos em FastAPI)

2. **`/opt/openmind-ai/`**
   - OpenMind AI Server (FastAPI original)
   - Migrado para `/root/MCP_SinapUm/services/openmind_service/`

## ✅ Após Remoção

Após remover as pastas antigas:

1. Verificar que o novo serviço continua funcionando
2. Atualizar referências em outros serviços (se houver)
3. Atualizar documentação
4. Manter os backups por segurança

## 🆘 Problemas

Se algo der errado após a remoção:

1. **Restaurar do backup** (veja seção acima)
2. **Verificar logs**: `docker logs openmind_service`
3. **Reiniciar serviço**: `docker compose restart` no novo local
4. **Verificar volumes**: `docker inspect openmind_service | grep Mounts`

