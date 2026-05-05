from __future__ import annotations

from app_billing.gateways.stripe_gateway import StripeGateway


class BillingService:
    """
    Fachada fina sobre o gateway Stripe — sem modelos Django.
    A camada de regras (``app_platform_billing``) compõe metadados e grava no ORM.
    """

    @staticmethod
    def create_customer(name: str, email: str, metadata: dict | None = None) -> str:
        customer = StripeGateway.create_customer(
            name=name,
            email=email,
            metadata=metadata,
        )
        return customer.id

    @staticmethod
    def create_subscription(
        customer_id: str, price_id: str, metadata: dict | None = None
    ):
        return StripeGateway.create_subscription(
            customer_id=customer_id,
            price_id=price_id,
            metadata=metadata,
        )

    @staticmethod
    def cancel_subscription(subscription_id: str):
        return StripeGateway.cancel_subscription(subscription_id)
