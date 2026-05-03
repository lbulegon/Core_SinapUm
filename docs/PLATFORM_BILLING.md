# Billing plataforma (multi-SaaS) — Core_SinapUm

Camada única de **produto → planos → cliente Stripe → assinatura → webhooks**.

## Objetivo

- **Um catálogo** de produtos (`SaaSProduct`) e planos (`CatalogPlan`) por produto.
- **Uma assinatura por par (utilizador, produto)** (`PlatformSubscription`), alinhada ao Stripe.
- **Um processador de webhook** (`stripe_dispatch`) partilhado por todos os endpoints HTTP que recebem eventos Stripe.

## Apps

| Componente | Caminho |
|------------|---------|
| Billing | `app_platform_billing/` |
| SinapLint | Rotas legadas `/api/sinaplint/saas/billing/*` delegam nas views de compatibilidade (`SinapLintCompat*`) que leem/escrevem só o catálogo plataforma (produto `sinaplint`). |

## Variáveis de ambiente

`STRIPE_SECRET_KEY`, `STRIPE_WEBHOOK_SECRET`, `STRIPE_SUCCESS_URL`, `STRIPE_CANCEL_URL` (ver `setup/settings.py`).

## API HTTP

Base: **`/api/platform/billing/`**

| Método | Rota | Descrição |
|--------|------|-----------|
| GET | `plans/?product=<slug>` | Planos públicos do produto |
| POST | `checkout/` | JSON: `product` (slug), `plan_slug` **ou** `price_id` |
| POST | `webhooks/stripe/` | Webhook Stripe |

### Checkout (exemplo)

```json
POST /api/platform/billing/checkout/
{
  "product": "sinaplint",
  "plan_slug": "pro"
}
```

Metadados na sessão e na subscrição: `user_id`, `product_slug`.

## Webhook

URL recomendado: `https://<seu-core>/api/platform/billing/webhooks/stripe/`

A URL legada **`/api/sinaplint/saas/webhooks/stripe/`** chama o **mesmo** processador (`verify_and_process_stripe_request`).

Comportamento: eventos `checkout.session.completed`, `customer.subscription.updated` / `deleted` atualizam **`PlatformSubscription`**. Se faltar `product_slug` nos metadados Stripe, assume-se **`sinaplint`** (sessões antigas).

## SinapLint — dados e limites

- Planos e limites: `CatalogPlan` (campo `limits` JSON: `max_analyses_per_month`, `max_repos`, …).
- Uso mensal / repositórios: código em `app_sinaplint` lê o plano efectivo via `get_effective_plan()` → `CatalogPlan`.

## Semear planos (incl. SinapLint)

```bash
python manage.py migrate
python manage.py sinaplint_seed_plans
```

(`seed_platform_billing_from_sinaplint` é alias idempotente do mesmo catálogo.)

## Novo SaaS (ex.: MotoPro)

1. Admin: `SaaSProduct` + `CatalogPlan` com `stripe_price_id` reais.
2. Checkout: `POST /api/platform/billing/checkout/` com `product` + `plan_slug` ou `price_id`.
3. Limites: JSON em `CatalogPlan.limits`; a app do produto aplica as quotas.

## Extensões sugeridas

- Helper `get_effective_limits(user, product_slug)` partilhado.
- Documentar Price IDs test/live no teu processo interno de billing.
