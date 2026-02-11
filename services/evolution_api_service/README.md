# Evolution API — Core_SinapUm

Integracao WhatsApp via Evolution API. Suporte a modo **image** (estavel) e modo **build** (patch 21/jan PR #2365 para QR code).

## Modo Image (estavel)

Usa imagem Docker Hub com tag fixa. **Nunca usar latest.**

```bash
cp .env.example .env
# Edite .env com suas credenciais
./scripts/up.sh
```

## Modo Build (patch 21/jan)

Builda a partir do source com o patch do PR #2365 (corrige loop infinito de reconexao do QR).

```bash
cp .env.example .env
# Edite .env
./scripts/up-build.sh
```

## Como ver QR

### Endpoint (curl)

```bash
# Carregue .env
source .env 2>/dev/null || true

# Criar instancia
curl -X POST http://localhost:8004/instance/create \
  -H "apikey: $EVOLUTION_API_KEY" -H "Content-Type: application/json" \
  -d '{"instanceName":"minha-instancia","qrcode":true,"integration":"WHATSAPP-BAILEYS"}'

# Obter QR
curl http://localhost:8004/instance/connect/minha-instancia \
  -H "apikey: $EVOLUTION_API_KEY"
```

O payload contem `base64` ou `pairingCode`. Logs mostram `qrcode.count` quando QR e gerado.

### Manager

Se o Evolution Manager estiver instalado, aponte para `EVOLUTION_SERVER_URL` (ex: http://localhost:8004).

## Troubleshooting

### Redis desconectado

- Verifique: `docker compose ps` — redis deve estar healthy
- Se necessario, reinicie: `./scripts/down.sh` e `./scripts/up.sh`

### Sessao corrompida (reset volumes)

```bash
./scripts/reset_session.sh --force
./scripts/up.sh
```

### CONFIG_SESSION_PHONE_VERSION

Manter **descomentado / nao setar** por padrao. A API detecta automaticamente. Fixar pode causar falhas no QR.

### Loop/reconnect infinito no QR

Use o modo build (patch 21/jan):

```bash
./scripts/up-build.sh
```

## Scripts

| Script | Uso |
|--------|-----|
| `up.sh` | Sobe modo image |
| `up-build.sh` | Sobe modo build (patch 21/jan) |
| `down.sh` | Para containers |
| `logs.sh` | Tail dos logs |
| `smoke_test.sh` | Health + create + connect (valida QR) |
| `reset_session.sh --force` | Apaga volumes de sessao |
| `rollback.sh --force` | Restaura backup e sobe modo image |
| `diagnose_qr.sh` | Diagnostico detalhado do QR |

## Configuracao (.env)

Variaveis obrigatorias: `EVOLUTION_SERVER_URL`, `EVOLUTION_API_KEY`, `EVOLUTION_DB_URI`, `EVOLUTION_WEBHOOK_URL`.

Copie `.env.example` para `.env` e preencha. **Nunca commitar .env.**

## Rollback

Backup: `docker-compose.yml.bak`

```bash
./scripts/rollback.sh --force
```

## Referencias

- [Evolution API Docs](https://doc.evolution-api.com/)
- [Evolution API GitHub](https://github.com/EvolutionAPI/evolution-api)
- [PR #2365 — Fix QR loop](https://github.com/EvolutionAPI/evolution-api/pull/2365)
