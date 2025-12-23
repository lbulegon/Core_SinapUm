# ✅ Resumo da Renomeação: MCP_SinapUm → Core_SinapUm

## 📋 Alterações Realizadas

### 1. ✅ Pasta Renomeada
- `/root/MCP_SinapUm` → `/root/Core_SinapUm`

### 2. ✅ Scripts Atualizados
- `/root/restart_all_services.sh`
- `/root/reset_all_services.sh`
- `/root/Core_SinapUm/restart_services.sh`
- `/root/Core_SinapUm/reset_services.sh`

### 3. ✅ Código Python Atualizado (ÉVORA)
- `evora/app_marketplace/services.py`
- `evora/setup/settings.py`
- `evora/conectar_whatsapp.py`
- `evora/test_sistema_imagens.py`
- `evora/environment_variables.example`

### 4. ✅ Documentação Atualizada
- `evora/GUIA_CONECTAR_WHATSAPP.md`
- `evora/DEPLOY_WHATSAPP_RAILWAY.md`
- `evora/CORRECOES_MCP_SINAPUM.md`
- `Core_SinapUm/README.md`
- E outros arquivos de documentação

### 5. ✅ Docker Compose Atualizado
- `Core_SinapUm/services/evolution_api/docker-compose.yml`
- `Core_SinapUm/services/ddf_service/docker-compose.yml`

## 🔄 Próximos Passos

### 1. Renomear Repositório no GitHub

O repositório atual está em: `https://github.com/lbulegon/SinapUm.git`

**Opção A: Renomear o repositório existente (Recomendado)**
1. Acesse: https://github.com/lbulegon/SinapUm/settings
2. Vá em "General" → "Repository name"
3. Altere de `SinapUm` para `Core_SinapUm`
4. Clique em "Rename"

**Opção B: Criar novo repositório**
1. Crie um novo repositório chamado `Core_SinapUm`
2. Atualize o remote:
   ```bash
   cd /root/Core_SinapUm
   git remote set-url origin https://github.com/lbulegon/Core_SinapUm.git
   ```

### 2. Atualizar Referências Restantes

Ainda existem algumas referências a `MCP_SinapUm` em arquivos de documentação dentro de `Core_SinapUm`. 
Para atualizar todas de uma vez, execute:

```bash
cd /root/Core_SinapUm
find . -type f \( -name "*.md" -o -name "*.sh" -o -name "*.py" \) -exec sed -i 's/MCP_SinapUm/Core_SinapUm/g' {} \;
```

### 3. Reiniciar Serviços

```bash
# Reiniciar todos os serviços
cd /root
./restart_all_services.sh

# Ou manualmente:
cd /root/Core_SinapUm
docker compose up -d

cd /root/Core_SinapUm/services/evolution_api
docker compose up -d

cd /root/Core_SinapUm/services/sparkscore_service
docker compose up -d

cd /root/Core_SinapUm/services/ddf_service
docker compose up -d
```

### 4. Fazer Commit e Push das Alterações

```bash
cd /root/Core_SinapUm
git add .
git commit -m "Renomear projeto de MCP_SinapUm para Core_SinapUm"
git push origin main
```

## ⚠️ Observações Importantes

1. **Docker Compose**: Usa caminhos relativos, então não precisa alterar paths
2. **Volumes Docker**: Não são afetados (usam nomes, não caminhos)
3. **Banco de Dados**: Não é afetado
4. **Serviços em Execução**: Foram parados antes da renomeação

## ✅ Status

- ✅ Pasta renomeada
- ✅ Scripts principais atualizados
- ✅ Código Python atualizado
- ✅ Documentação principal atualizada
- ✅ Docker Compose atualizado
- ⏳ Renomear repositório no GitHub (pendente)
- ⏳ Atualizar referências restantes em documentação (opcional)
- ⏳ Reiniciar serviços (pendente)

## 📝 Notas

- Alguns arquivos de documentação histórica ainda podem conter referências a `MCP_SinapUm` por contexto histórico
- O repositório Git precisa ser renomeado no GitHub para refletir a mudança
- Todos os serviços foram parados e precisam ser reiniciados após a renomeação


