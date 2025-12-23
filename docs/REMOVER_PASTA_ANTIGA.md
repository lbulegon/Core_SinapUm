# Remover Pasta Antiga /root/evolution_api

A pasta antiga `/root/evolution_api/` ainda existe e precisa ser removida.

## ✅ Execute este comando:

```bash
python3 /root/MCP_SinapUm/services/evolution_api_service/remover_pasta_antiga.py
```

Ou manualmente:

```bash
rm -rf /root/evolution_api
```

## ✅ Verificação

Após remover, verifique:

```bash
ls -la /root/ | grep evolution_api
```

Se não aparecer nada, a pasta foi removida com sucesso!

