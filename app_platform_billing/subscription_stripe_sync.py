"""
Lógica compartilhada: alinhar ``PlatformSubscription`` a um objeto/dict de Subscription Stripe.

Usado pelo ``manage.py sync_stripe_subscription`` e pelos webhooks quando os metadados
vêm vazios, desde que o catálogo tenha ``stripe_price_id`` correto e o Customer
tenha e-mail igual a um ``User`` (ou já exista linha com o mesmo ``cus_`` + produto).
"""

from __future__ import annotations

import stripe
from django.conf import settings
from django.contrib.auth import get_user_model

from app_platform_billing.models import CatalogPlan, PlatformSubscription
from app_platform_billing.stripe_utils import (
    stripe_obj_get,
    stripe_period_end_aware,
    stripe_subscription_price_id,
)


def customer_id_from_stripe_subscription(sub: object) -> str:
    cust = stripe_obj_get(sub, "customer")
    if isinstance(cust, str):
        return cust
    if cust is None:
        return ""
    return str(stripe_obj_get(cust, "id") or cust)


def stripe_customer_email(customer_id: str) -> str | None:
    if not customer_id or not getattr(settings, "STRIPE_SECRET_KEY", ""):
        return None
    try:
        stripe.api_key = settings.STRIPE_SECRET_KEY
        cust = stripe.Customer.retrieve(customer_id)
    except Exception:
        return None
    if isinstance(cust, dict):
        em = cust.get("email")
    else:
        em = getattr(cust, "email", None)
    return em.strip() if isinstance(em, str) and em.strip() else None


def apply_stripe_payload_to_platform_subscription(
    ps: PlatformSubscription, sub: object
) -> None:
    price_id = stripe_subscription_price_id(sub)
    plan = None
    if price_id:
        plan = CatalogPlan.objects.filter(
            product=ps.product,
            stripe_price_id=price_id,
        ).first()

    cid = customer_id_from_stripe_subscription(sub)
    sub_id = stripe_obj_get(sub, "id") or ""
    status_s = stripe_obj_get(sub, "status") or "active"

    ps.stripe_customer_id = cid or ps.stripe_customer_id
    ps.stripe_subscription_id = sub_id or ps.stripe_subscription_id
    ps.status = str(status_s)
    ps.plan = plan
    ps.current_period_end = stripe_period_end_aware(sub)
    ps.save(
        update_fields=[
            "stripe_customer_id",
            "stripe_subscription_id",
            "status",
            "plan",
            "current_period_end",
            "updated_at",
        ]
    )


def upsert_platform_subscription_from_stripe_payload(
    sub: object,
) -> PlatformSubscription | None:
    """
    Cria ou atualiza ``PlatformSubscription`` usando customer + price do catálogo
    (sem depender de metadata na subscription).
    """
    subscription_id = stripe_obj_get(sub, "id") or ""
    if not subscription_id:
        return None

    cid = customer_id_from_stripe_subscription(sub)
    if not cid:
        return None

    price_id = stripe_subscription_price_id(sub)
    if not price_id:
        return None

    plan = (
        CatalogPlan.objects.filter(stripe_price_id=price_id)
        .select_related("product")
        .first()
    )
    if not plan:
        return None

    product = plan.product

    ps = (
        PlatformSubscription.objects.filter(
            stripe_customer_id=cid,
            product=product,
        )
        .select_related("user", "product")
        .first()
    )
    if ps:
        apply_stripe_payload_to_platform_subscription(ps, sub)
        return ps

    email = stripe_customer_email(cid)
    if not email:
        return None

    User = get_user_model()
    user = User.objects.filter(email__iexact=email).first()
    if not user:
        return None

    ps, _ = PlatformSubscription.objects.update_or_create(
        user=user,
        product=product,
        defaults={
            "stripe_customer_id": cid,
            "stripe_subscription_id": subscription_id,
        },
    )
    apply_stripe_payload_to_platform_subscription(ps, sub)
    return ps


def infer_product_slug_from_subscription_price(sub: object) -> str | None:
    """Resolve slug do SaaSProduct pelo stripe_price_id da subscription."""
    price_id = stripe_subscription_price_id(sub)
    if not price_id:
        return None
    plan = (
        CatalogPlan.objects.filter(stripe_price_id=price_id)
        .select_related("product")
        .first()
    )
    if not plan:
        return None
    return plan.product.slug
