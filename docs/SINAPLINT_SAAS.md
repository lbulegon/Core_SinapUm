# SinapLint SaaS (Django)

Blueprint integrado no `app_sinaplint`: **planos**, **Stripe**, **API keys por utilizador**, **uso mensal**.

## Rotas

| Método | URL | Descrição |
|--------|-----|-----------|
| GET | `/api/sinaplint/saas/billing/plans/` | Planos públicos (JSON) |
| POST | `/api/sinaplint/saas/billing/checkout/` | Cria sessão Stripe Checkout (autenticado) |
| POST | `/api/sinaplint/saas/webhooks/stripe/` | Webhook Stripe (sem CSRF) |
| POST | `/api/sinaplint/saas/v1/analyze/` | Análise com limite mensal (autenticado ou `X-API-Key`). Opcional: `repository_id`, `repo_url`, `repo_name`, `commit_hash`, `branch` para gravar histórico. |
| GET | `/api/sinaplint/saas/dashboard/summary/` | Uso + plano |
| GET | `/api/sinaplint/saas/dashboard/history/` | Lista de análises persistidas |
| GET | `/api/sinaplint/saas/dashboard/billing/` | Plano + estado Stripe |
| GET | `/api/sinaplint/saas/dashboard/overview/` | Agregado (summary + history + billing) |

## Modelos

- **Plan** — `stripe_price_id`, `max_analyses_per_month`, `max_repos`
- **Subscription** — `status` (substitui o antigo boolean `active`)
- **Repository** — por utilizador, URL única por user
- **Analysis** — resultado JSON + score; **AnalysisDelta** opcional (1:1)

Migração `0002_repository_analysis_delta_plan_sub` aplica renomeação `price_id` → `stripe_price_id` e novos modelos.

## Frontend

`tools/sinaplint-landing/` — rotas `/` (demo clone) e `/dashboard` (Recharts + cartões). Proxy Vite: `VITE_API_TARGET` (default `http://127.0.0.1:8000`); para o servidor de demo na 8765, `VITE_API_TARGET=http://127.0.0.1:8765 npm run dev`.

## Variáveis de ambiente

- `STRIPE_SECRET_KEY`, `STRIPE_WEBHOOK_SECRET`
- `STRIPE_SUCCESS_URL`, `STRIPE_CANCEL_URL` (opcional)

## Arranque

```bash
python manage.py migrate app_sinaplint
python manage.py sinaplint_seed_plans
```

Preencher `price_id` dos planos Pro/Scale no Admin (Stripe Dashboard → Prices).

## Autenticação

- Sessão Django ou **header `X-API-Key`** (middleware `SinapLintAPIKeyMiddleware` após login).

## Coexistência

O fluxo **SinapLint Cloud** existente (`SinapLintTenant` em `app_sinapcore`, `/api/sinaplint/`) mantém-se; este módulo segue o modelo **User** + Stripe descrito no blueprint SaaS.
