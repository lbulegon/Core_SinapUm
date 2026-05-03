"""
Verificação de assinatura Stripe + despacho único para todos os eventos suportados.
"""

from __future__ import annotations

from django.conf import settings
from django.http import HttpResponse

from app_platform_billing.stripe_handlers import (
    mark_platform_subscription_canceled,
    sync_checkout_completed,
    sync_subscription_updated,
)


def process_stripe_event(event: dict) -> None:
    et = event["type"]
    data = event["data"]["object"]
    default_product = "sinaplint"

    if et == "checkout.session.completed":
        meta = data.get("metadata") or {}
        slug = meta.get("product_slug") or default_product
        sync_checkout_completed(data, str(slug))
    elif et == "customer.subscription.updated":
        meta = data.get("metadata") or {}
        slug = meta.get("product_slug") or default_product
        sync_subscription_updated(data, str(slug))
    elif et == "customer.subscription.deleted":
        mark_platform_subscription_canceled(data)


def verify_and_process_stripe_request(payload: bytes, sig_header: str) -> HttpResponse:
    if not getattr(settings, "STRIPE_WEBHOOK_SECRET", None):
        return HttpResponse("Webhook não configurado", status=503)

    try:
        import stripe
    except ImportError:
        return HttpResponse("stripe não instalado", status=503)

    stripe.api_key = getattr(settings, "STRIPE_SECRET_KEY", "")

    try:
        event = stripe.Webhook.construct_event(
            payload,
            sig_header,
            settings.STRIPE_WEBHOOK_SECRET,
        )
    except ValueError:
        return HttpResponse("payload inválido", status=400)
    except Exception as e:
        if "Signature" in type(e).__name__:
            return HttpResponse("assinatura inválida", status=400)
        raise

    process_stripe_event(event)
    return HttpResponse(status=200)
