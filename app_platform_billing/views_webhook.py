"""Webhook Stripe — um único fluxo via ``stripe_dispatch``."""

from __future__ import annotations

from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_exempt

from app_platform_billing.stripe_dispatch import verify_and_process_stripe_request


@method_decorator(csrf_exempt, name="dispatch")
class PlatformStripeWebhookView(View):
    def post(self, request, *args, **kwargs):
        return verify_and_process_stripe_request(
            request.body,
            request.META.get("HTTP_STRIPE_SIGNATURE", ""),
        )
