"""Rotas /api/platform/billing/"""

from django.urls import path

from app_platform_billing import views
from app_platform_billing.views_webhook import PlatformStripeWebhookView

urlpatterns = [
    path("plans/", views.PlansListView.as_view(), name="platform_billing_plans"),
    path("checkout/", views.CreateCheckoutSessionView.as_view(), name="platform_billing_checkout"),
    path("webhooks/stripe/", PlatformStripeWebhookView.as_view(), name="platform_billing_stripe_webhook"),
]
