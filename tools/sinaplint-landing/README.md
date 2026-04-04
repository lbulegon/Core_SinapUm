# Landing SinapLint (demo)

Interface para colar um URL GitHub público e ver score + grafo (requer o **servidor de demo**).

## 1. Servidor (outro terminal, na raiz do Core_SinapUm)

```bash
python3 tools/sinaplint-demo-server/server.py
```

## 2. Esta app

```bash
cd tools/sinaplint-landing
npm install
npm run dev
```

Abre `http://localhost:5173`. O Vite faz proxy de `/api` para o backend (por defeito `http://127.0.0.1:8000` — Django). Para o demo HTTP em 8765: `VITE_API_TARGET=http://127.0.0.1:8765 npm run dev`.

- **`/`** — demo “cola repo” (clone + análise).
- **`/dashboard`** — uso, billing e histórico (`GET /api/sinaplint/saas/dashboard/overview/`, requer sessão Django no mesmo origin).

## Requisito

O repositório clonado tem de ter `app_sinaplint/` na raiz (estrutura SinapLint).
