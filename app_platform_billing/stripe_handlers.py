"""Sincronização Stripe → PlatformSubscription (+ metadados por produto)."""

from __future__ import annotations

from django.conf import settings
from django.contrib.auth import get_user_model

from app_platform_billing.models import CatalogPlan, PlatformSubscription, SaaSProduct
from app_platform_billing.stripe_utils import stripe_obj_get, stripe_period_end_aware, stripe_subscription_price_id


def _user_from_meta(meta: dict):
    User = get_user_model()
    uid = meta.get("user_id")
    if not uid:
        return None
    try:
        return User.objects.get(pk=int(uid))
    except (User.DoesNotExist, ValueError, TypeError):
        return None


def sync_checkout_completed(session: dict, product_slug: str) -> None:
    meta = session.get("metadata") or {}
    user = _user_from_meta(meta)
    if not user:
        return

    product = SaaSProduct.objects.filter(slug=product_slug, is_active=True).first()
    if not product:
        return

    sub_id = session.get("subscription")
    customer_id = session.get("customer")
    if not sub_id or not customer_id:
        return

    import stripe

    stripe.api_key = settings.STRIPE_SECRET_KEY
    sub = stripe.Subscription.retrieve(sub_id, expand=["items.data.price"])
    price_id = stripe_subscription_price_id(sub)
    plan = None
    if price_id:
        plan = CatalogPlan.objects.filter(
            product=product,
            stripe_price_id=price_id,
        ).first()

    period_end = stripe_period_end_aware(sub)
    status_s = stripe_obj_get(sub, "status") or "active"

    PlatformSubscription.objects.update_or_create(
        user=user,
        product=product,
        defaults={
            "stripe_customer_id": customer_id,
            "stripe_subscription_id": sub_id,
            "plan": plan,
            "status": str(status_s),
            "current_period_end": period_end,
        },
    )


def sync_subscription_updated(sub_obj: dict, product_slug: str | None) -> None:
    User = get_user_model()
    meta = sub_obj.get("metadata") or {}
    if not product_slug:
        product_slug = meta.get("product_slug")

    if not product_slug:
        return

    product = SaaSProduct.objects.filter(slug=product_slug, is_active=True).first()
    if not product:
        return

    user = _user_from_meta(meta)
    customer_id = sub_obj.get("customer")
    sub_id = sub_obj.get("id")
    status_s = sub_obj.get("status")

    if not user and customer_id:
        row = (
            PlatformSubscription.objects.filter(
                stripe_customer_id=customer_id,
                product=product,
            )
            .values_list("user_id", flat=True)
            .first()
        )
        if row:
            user = User.objects.filter(pk=row).first()

    if not user:
        return

    price_id = stripe_subscription_price_id(sub_obj)
    plan = (
        CatalogPlan.objects.filter(product=product, stripe_price_id=price_id).first()
        if price_id
        else None
    )
    period_end = stripe_period_end_aware(sub_obj)

    PlatformSubscription.objects.update_or_create(
        user=user,
        product=product,
        defaults={
            "stripe_subscription_id": sub_id or "",
            "stripe_customer_id": customer_id or "",
            "plan": plan,
            "status": str(status_s) if status_s else "active",
            "current_period_end": period_end,
        },
    )


def mark_platform_subscription_canceled(sub_obj: dict) -> None:
    """Cancela por ``customer``; ``product_slug`` nos metadados ou fallback ``sinaplint``."""
    from app_platform_billing.catalog_limits import SINAPLINT_PRODUCT_SLUG

    meta = sub_obj.get("metadata") or {}
    product_slug = meta.get("product_slug") or SINAPLINT_PRODUCT_SLUG
    customer_id = sub_obj.get("customer")
    if not customer_id:
        return
    PlatformSubscription.objects.filter(
        stripe_customer_id=customer_id,
        product__slug=str(product_slug),
    ).update(status="canceled", stripe_subscription_id="")
