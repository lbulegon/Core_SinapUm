"""Lógica de criação de sessão Stripe Checkout (reutilizável por rotas SinapLint legadas)."""

from __future__ import annotations

from typing import TYPE_CHECKING

from django.conf import settings

from app_billing.services.billing_service import BillingService
from app_platform_billing.catalog_limits import get_platform_subscription, get_saas_product
from app_platform_billing.models import CatalogPlan, PlatformSubscription

if TYPE_CHECKING:
    from django.contrib.auth.models import AbstractUser


def stripe_available() -> bool:
    try:
        import stripe  # noqa: F401
    except ImportError:
        return False
    return bool(getattr(settings, "STRIPE_SECRET_KEY", None))


def create_checkout_session_url(
    user: AbstractUser,
    product_slug: str,
    *,
    price_id: str | None = None,
    plan_slug: str | None = None,
) -> tuple[str | None, str | None]:
    """
    Devolve ``(checkout_url, error_message)``.
    ``error_message`` preenchido em caso de falha (Stripe indisponível, plano inválido, etc.).
    """
    if not stripe_available():
        return None, "Stripe não configurado (STRIPE_SECRET_KEY ou pacote stripe)."

    import stripe

    stripe.api_key = settings.STRIPE_SECRET_KEY

    product = get_saas_product(product_slug)
    if not product:
        return None, "produto inválido ou inativo"

    resolved_price = price_id
    if not resolved_price and plan_slug:
        plan = CatalogPlan.objects.filter(
            product=product,
            slug=str(plan_slug),
            is_public=True,
        ).first()
        if plan and plan.stripe_price_id:
            resolved_price = plan.stripe_price_id
    if not resolved_price:
        return None, "price_id ou plan_slug com stripe_price_id obrigatório"

    success_url = getattr(
        settings,
        "STRIPE_SUCCESS_URL",
        "http://127.0.0.1:8000/api/platform/billing/success/",
    )
    cancel_url = getattr(
        settings,
        "STRIPE_CANCEL_URL",
        "http://127.0.0.1:8000/api/platform/billing/cancel/",
    )

    ps = get_platform_subscription(user.pk, product_slug)
    customer_id = ps.stripe_customer_id if ps and ps.stripe_customer_id else None

    if not customer_id:
        customer_id = BillingService.create_customer(
            name=user.get_full_name() or getattr(user, "username", "") or "",
            email=getattr(user, "email", "") or "",
            metadata={"user_id": str(user.pk), "product_slug": product.slug},
        )
        PlatformSubscription.objects.update_or_create(
            user=user,
            product=product,
            defaults={
                "stripe_customer_id": customer_id,
                "status": "none",
            },
        )

    session = stripe.checkout.Session.create(
        customer=customer_id,
        payment_method_types=["card"],
        mode="subscription",
        line_items=[{"price": resolved_price, "quantity": 1}],
        success_url=success_url + "?session_id={CHECKOUT_SESSION_ID}",
        cancel_url=cancel_url,
        metadata={
            "user_id": str(user.pk),
            "product_slug": product.slug,
        },
        subscription_data={
            "metadata": {
                "user_id": str(user.pk),
                "product_slug": product.slug,
            },
        },
    )
    url = session.url if session else None
    if not url:
        return None, "Stripe não devolveu URL de checkout."
    return str(url), None
