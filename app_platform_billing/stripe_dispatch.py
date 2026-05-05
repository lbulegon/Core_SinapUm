"""
Verificação de assinatura Stripe + despacho único para todos os eventos suportados.
"""

from __future__ import annotations

import logging

from django.http import HttpResponse

from app_billing.webhooks.stripe_webhook import parse_stripe_webhook_event
from app_platform_billing.stripe_handlers import (
    mark_platform_subscription_canceled,
    sync_checkout_completed,
    sync_subscription_updated,
)

logger = logging.getLogger(__name__)


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
    elif et == "invoice.paid":
        logger.info("Stripe invoice.paid: %s", data.get("id"))
    elif et == "invoice.payment_failed":
        logger.warning("Stripe invoice.payment_failed: %s", data.get("id"))


def verify_and_process_stripe_request(payload: bytes, sig_header: str) -> HttpResponse:
    event, err = parse_stripe_webhook_event(payload, sig_header)
    if err is not None:
        return err
    assert event is not None
    process_stripe_event(event)
    return HttpResponse(status=200)
