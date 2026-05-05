"""
Sincronização manual Stripe → ``PlatformSubscription`` (reconciliação / drift).

Use quando o webhook falhou, há dúvida de estado ou precisa alinhar o BD à Stripe.
"""

from __future__ import annotations

from dataclasses import dataclass

import stripe
from django.conf import settings

from app_platform_billing.models import CatalogPlan, PlatformSubscription
from app_platform_billing.stripe_handlers import sync_subscription_updated
from app_platform_billing.stripe_utils import stripe_obj_get, stripe_subscription_price_id
from app_platform_billing.subscription_stripe_sync import (
    apply_stripe_payload_to_platform_subscription,
    upsert_platform_subscription_from_stripe_payload,
)


@dataclass
class StripeSubscriptionSyncResult:
    ok: bool
    message: str
    platform_subscription: PlatformSubscription | None = None


def sync_subscription(subscription_id: str) -> StripeSubscriptionSyncResult:
    """
    Obtém a subscription na Stripe e atualiza o ``PlatformSubscription`` correspondente.

    1) Linha com o mesmo ``stripe_subscription_id`` → atualiza.
    2) ``sync_subscription_updated`` (metadados ``user_id`` + ``product_slug`` ou catálogo).
    3) Sem metadata: ``customer`` + preço do catálogo → ver ``subscription_stripe_sync``.
    """
    key = getattr(settings, "STRIPE_SECRET_KEY", "") or ""
    if not key.strip():
        return StripeSubscriptionSyncResult(
            ok=False,
            message="STRIPE_SECRET_KEY não configurada.",
            platform_subscription=None,
        )

    stripe.api_key = key

    try:
        sub = stripe.Subscription.retrieve(
            subscription_id,
            expand=["items.data.price"],
        )
    except Exception as e:
        return StripeSubscriptionSyncResult(
            ok=False,
            message=f"Stripe: {e}",
            platform_subscription=None,
        )

    ps = (
        PlatformSubscription.objects.filter(stripe_subscription_id=subscription_id)
        .select_related("product", "user")
        .first()
    )
    if ps:
        apply_stripe_payload_to_platform_subscription(ps, sub)
        return StripeSubscriptionSyncResult(
            ok=True,
            message="Sincronizado (assinatura encontrada por stripe_subscription_id).",
            platform_subscription=ps,
        )

    meta = stripe_obj_get(sub, "metadata") or {}
    product_slug = meta.get("product_slug")
    sync_subscription_updated(sub, product_slug)

    ps2 = (
        PlatformSubscription.objects.filter(stripe_subscription_id=subscription_id)
        .select_related("product", "user")
        .first()
    )
    if ps2:
        return StripeSubscriptionSyncResult(
            ok=True,
            message="Sincronizado (via webhook handler / metadados / catálogo).",
            platform_subscription=ps2,
        )

    ps3 = upsert_platform_subscription_from_stripe_payload(sub)
    if ps3:
        return StripeSubscriptionSyncResult(
            ok=True,
            message=(
                "Sincronizado (customer + preço do catálogo). "
                "Associação por stripe_customer_id + CatalogPlan.stripe_price_id e/ou e-mail do Customer."
            ),
            platform_subscription=ps3,
        )

    price_id = stripe_subscription_price_id(sub)
    if price_id and not CatalogPlan.objects.filter(stripe_price_id=price_id).exists():
        return StripeSubscriptionSyncResult(
            ok=False,
            message=(
                f"Nenhum CatalogPlan com stripe_price_id={price_id}. "
                "Configure o Price no Admin (app_platform_billing) para o produto correto."
            ),
            platform_subscription=None,
        )

    return StripeSubscriptionSyncResult(
        ok=False,
        message=(
            "Não foi possível associar: não há "
            "PlatformSubscription com mesmo stripe_customer_id + produto do catálogo, "
            "ou o e-mail do Customer na Stripe não bate com nenhum User Django."
        ),
        platform_subscription=None,
    )
