"""
Checkout Stripe e início de assinatura.
"""

from __future__ import annotations

from django.conf import settings
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status

from app_sinaplint.models_billing import Plan, Subscription


def _stripe_available() -> bool:
    try:
        import stripe  # noqa: F401
    except ImportError:
        return False
    return bool(getattr(settings, "STRIPE_SECRET_KEY", None))


class CreateCheckoutSessionView(APIView):
    """POST ``{"price_id": "price_..."}`` ou ``{"plan_slug": "pro"}`` — devolve ``{"url": "..."}``."""

    permission_classes = [IsAuthenticated]

    def post(self, request: Request) -> Response:
        if not _stripe_available():
            return Response(
                {"error": "Stripe não configurado (STRIPE_SECRET_KEY ou pacote stripe)."},
                status=status.HTTP_503_SERVICE_UNAVAILABLE,
            )

        import stripe

        stripe.api_key = settings.STRIPE_SECRET_KEY

        price_id = request.data.get("price_id")
        plan_slug = request.data.get("plan_slug")
        if not price_id and plan_slug:
            plan = Plan.objects.filter(slug=str(plan_slug), is_public=True).first()
            if plan and plan.stripe_price_id:
                price_id = plan.stripe_price_id
        if not price_id:
            return Response(
                {"error": "price_id ou plan_slug válido obrigatório"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        success_url = getattr(
            settings,
            "STRIPE_SUCCESS_URL",
            "http://localhost:8000/sinaplint/billing/success/",
        )
        cancel_url = getattr(
            settings,
            "STRIPE_CANCEL_URL",
            "http://localhost:8000/sinaplint/billing/cancel/",
        )

        user = request.user
        customer_id = None
        sub = Subscription.objects.filter(user=user).first()
        if sub and sub.stripe_customer_id:
            customer_id = sub.stripe_customer_id
        else:
            cust = stripe.Customer.create(
                email=getattr(user, "email", None) or None,
                metadata={"user_id": str(user.pk)},
            )
            customer_id = cust.id
            Subscription.objects.update_or_create(
                user=user,
                defaults={
                    "stripe_customer_id": customer_id,
                    "status": "active",
                },
            )

        session = stripe.checkout.Session.create(
            customer=customer_id,
            payment_method_types=["card"],
            mode="subscription",
            line_items=[{"price": price_id, "quantity": 1}],
            success_url=success_url + "?session_id={CHECKOUT_SESSION_ID}",
            cancel_url=cancel_url,
            metadata={"user_id": str(user.pk)},
            subscription_data={
                "metadata": {"user_id": str(user.pk)},
            },
        )
        return Response({"url": session.url}, status=status.HTTP_200_OK)


class PlansListView(APIView):
    """Lista planos públicos (para a landing)."""

    permission_classes = [AllowAny]

    def get(self, request: Request) -> Response:
        plans = Plan.objects.filter(is_public=True).values(
            "id",
            "name",
            "slug",
            "stripe_price_id",
            "max_analyses_per_month",
            "max_repos",
            "sort_order",
        )
        return Response(list(plans))
