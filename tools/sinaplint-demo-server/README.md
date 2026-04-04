# Servidor de demo SinapLint

Executa `git clone` (shallow) e `python -m app_sinaplint check --json` no repositório clonado.

## Arranque

Na raiz do **Core_SinapUm** (onde existe `app_sinaplint/`):

```bash
python3 tools/sinaplint-demo-server/server.py
```

Variáveis opcionais: `SINAPLINT_DEMO_HOST`, `SINAPLINT_DEMO_PORT` (default `8765`).

## Segurança

Destinado a **desenvolvimento local** ou rede confiável. Valida URL GitHub HTTPS; não exponha sem reverse proxy e rate limit em produção pública.
