from __future__ import annotations

import stripe
from django.conf import settings


def _configure_stripe() -> None:
    stripe.api_key = getattr(settings, "STRIPE_SECRET_KEY", "") or ""


class StripeGateway:
    @staticmethod
    def create_customer(name: str, email: str, metadata: dict | None = None) -> stripe.Customer:
        _configure_stripe()
        return stripe.Customer.create(
            name=name,
            email=email or None,
            metadata=metadata or {},
        )

    @staticmethod
    def create_subscription(
        customer_id: str, price_id: str, metadata: dict | None = None
    ) -> stripe.Subscription:
        _configure_stripe()
        return stripe.Subscription.create(
            customer=customer_id,
            items=[{"price": price_id}],
            metadata=metadata or {},
        )

    @staticmethod
    def cancel_subscription(subscription_id: str) -> stripe.Subscription:
        _configure_stripe()
        return stripe.Subscription.delete(subscription_id)
