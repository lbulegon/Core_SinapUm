# Migração de Volumes - Evolution API

## Situação Atual

Os volumes de dados do Evolution API estão em `/root/evolution_api/`:
- `pg_data/` - Dados PostgreSQL
- `redis_data/` - Dados Redis  
- `instances/` - Instâncias WhatsApp
- `storage/` - Armazenamento de arquivos
- `mongo_data/` - Dados MongoDB (se usado)

## Opções

### Opção 1: Manter volumes em /root/evolution_api/ (Recomendado)

O `docker-compose.yml` já está configurado para usar os volumes do local original:

```yaml
volumes:
  - /root/evolution_api/pg_data:/var/lib/postgresql/data
  - /root/evolution_api/redis_data:/data
  - /root/evolution_api/instances:/evolution/instances
```

**Vantagens:**
- Não quebra containers ativos
- Não precisa mover grandes volumes
- Funciona imediatamente

### Opção 2: Mover volumes para estrutura de serviços

Se quiser mover os volumes para a estrutura de serviços:

1. **Parar containers:**
```bash
cd /root/evolution_api
docker compose down
```

2. **Mover volumes:**
```bash
mv /root/evolution_api/pg_data /root/MCP_SinapUm/services/evolution_api_service/
mv /root/evolution_api/redis_data /root/MCP_SinapUm/services/evolution_api_service/
mv /root/evolution_api/instances /root/MCP_SinapUm/services/evolution_api_service/
mv /root/evolution_api/storage /root/MCP_SinapUm/services/evolution_api_service/
```

3. **Atualizar docker-compose.yml:**
```yaml
volumes:
  - ./pg_data:/var/lib/postgresql/data
  - ./redis_data:/data
  - ./instances:/evolution/instances
```

4. **Remover pasta antiga:**
```bash
rm -rf /root/evolution_api
```

5. **Subir containers:**
```bash
cd /root/MCP_SinapUm/services/evolution_api_service
docker compose up -d
```

## Recomendação

**Manter volumes em `/root/evolution_api/`** até que seja necessário mover, pois:
- Volumes são grandes
- Podem estar em uso
- Mover pode causar downtime

