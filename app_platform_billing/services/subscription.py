"""Regras de assinatura na plataforma — delega execução Stripe a ``app_billing``."""

from __future__ import annotations

from django.conf import settings

from app_billing.services.billing_service import BillingService
from app_platform_billing.models import CatalogPlan, PlatformSubscription


class PlatformSubscriptionService:
    @staticmethod
    def subscribe(tenant: PlatformSubscription, plano: CatalogPlan):
        """
        Cria assinatura Stripe direta (customer + subscription).
        Fluxos via Checkout continuam em ``checkout_service.create_checkout_session_url``.
        """
        if not plano.stripe_price_id:
            raise ValueError("Plano sem stripe_price_id configurado.")

        user = tenant.user
        display_name = user.get_full_name() or getattr(user, "username", "") or ""
        email = getattr(user, "email", "") or ""

        meta_base = {
            "user_id": str(user.pk),
            "product_slug": tenant.product.slug,
        }

        if not tenant.stripe_customer_id:
            customer_id = BillingService.create_customer(
                name=display_name,
                email=email,
                metadata=meta_base,
            )
            tenant.stripe_customer_id = customer_id
            tenant.save(update_fields=["stripe_customer_id", "updated_at"])

        return BillingService.create_subscription(
            customer_id=tenant.stripe_customer_id,
            price_id=plano.stripe_price_id,
            metadata=meta_base,
        )

    @staticmethod
    def cancel_stripe_subscription(subscription_id: str):
        if not getattr(settings, "STRIPE_SECRET_KEY", None):
            raise RuntimeError("Stripe não configurado (STRIPE_SECRET_KEY).")
        return BillingService.cancel_subscription(subscription_id)
