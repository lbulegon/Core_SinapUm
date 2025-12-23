# Recuperar OpenMind Após Remoção Prematura

## ⚠️ Situação

A pasta `/opt/openmind-ai` foi removida antes da migração ser executada. Agora precisamos recuperar a aplicação.

## 🔍 Opções de Recuperação

### Opção 1: Restaurar do Backup (Recomendado)

Se você tem um backup da pasta `/opt/openmind-ai`:

```bash
# 1. Listar backups disponíveis
ls -lh /root/backup_openmind_*

# 2. Restaurar o backup mais recente
# Se for .tar.gz
tar -xzf /root/backup_openmind_remocao_*_openmind-ai.tar.gz -C /tmp/

# 3. Encontrar onde foi extraído
find /tmp -type d -name "openmind-ai" 2>/dev/null

# 4. Executar migração apontando para o local restaurado
cd /root/MCP_SinapUm/services
SOURCE_DIR=/tmp/openmind-ai ./migrar_openmind_unificado.sh
```

### Opção 2: Usar Script de Recuperação Automatizado

```bash
cd /root/MCP_SinapUm/services
chmod +x recuperar_openmind.sh
./recuperar_openmind.sh
```

Este script irá:
- Procurar backups automaticamente
- Verificar se há processos rodando
- Verificar containers Docker
- Verificar porta 8000
- Tentar encontrar a aplicação em outros locais

### Opção 3: Verificar se Está Rodando de Outro Lugar

```bash
# Ver processos uvicorn
ps aux | grep uvicorn

# Ver porta 8000
sudo lsof -i :8000

# Ver containers
docker ps -a | grep openmind

# Se encontrar processo, verificar diretório de trabalho
pwdx $(pgrep -f "uvicorn.*openmind")
```

### Opção 4: Recriar do Zero (Último Recurso)

Se não houver backup e não encontrar a aplicação em outro lugar, será necessário recriar:

1. **Clonar/criar aplicação FastAPI básica**
2. **Copiar estrutura do OpenMind AI** (se tiver acesso ao código fonte)
3. **Configurar variáveis de ambiente**
4. **Subir o serviço**

## 📋 Checklist de Recuperação

- [ ] Verificar se há backup em `/root/backup_openmind_*`
- [ ] Verificar processos rodando (`ps aux | grep uvicorn`)
- [ ] Verificar containers Docker (`docker ps -a`)
- [ ] Verificar porta 8000 (`sudo lsof -i :8000`)
- [ ] Executar script de recuperação (`./recuperar_openmind.sh`)
- [ ] Restaurar do backup se encontrado
- [ ] Executar migração após restaurar

## 🚀 Após Recuperar

Depois de recuperar a aplicação:

```bash
cd /root/MCP_SinapUm/services
./migrar_openmind_unificado.sh
```

Ou se restaurou em local diferente:

```bash
SOURCE_DIR=/caminho/restaurado ./migrar_openmind_unificado.sh
```

## 💡 Prevenção Futura

**Sempre execute a migração ANTES de remover pastas antigas!**

Ordem correta:
1. ✅ Executar migração
2. ✅ Verificar que novo serviço está funcionando
3. ✅ Testar endpoints
4. ✅ Confirmar integração
5. ✅ **SÓ ENTÃO** remover pastas antigas

