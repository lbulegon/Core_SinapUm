# Evolution API v2.1.1

Instalação da Evolution API versão estável 2.1.1 usando Docker Compose.

## Configuração

As configurações foram baseadas nas variáveis do `.env` do projeto:
- `EVOLUTION_BASE_URL`: http://69.169.102.84:8004
- `EVOLUTION_API_KEY`: GKvy6psn-8HHpBQ4HAHKFOXnwjHR-oSzeGZzCaws0xg
- Porta: 8004 (mapeada para 8080 no container)

## Iniciar o serviço

```bash
cd /root/Core_SinapUm/services/evolution_api_service
docker compose up -d
```

## Parar o serviço

```bash
docker compose down
```

## Ver logs

```bash
docker compose logs -f evolution-api
```

## Verificar status

```bash
docker compose ps
curl http://localhost:8004/
```

## Documentação

- [Evolution API Docs](https://doc.evolution-api.com/)
- [GitHub Repository](https://github.com/EvolutionAPI/evolution-api)

