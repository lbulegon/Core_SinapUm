"""Rotas SinapLint SaaS (billing, webhook, análise com limite, dashboard)."""

from django.urls import path

from app_platform_billing.views import SinapLintCompatCheckoutView, SinapLintCompatPlansView
from app_platform_billing.views_webhook import PlatformStripeWebhookView

from app_sinaplint import views_dashboard, views_saas_analyze

urlpatterns = [
    path("billing/checkout/", SinapLintCompatCheckoutView.as_view(), name="sinaplint_checkout"),
    path("billing/plans/", SinapLintCompatPlansView.as_view(), name="sinaplint_plans"),
    path("webhooks/stripe/", PlatformStripeWebhookView.as_view(), name="sinaplint_stripe_webhook"),
    path("v1/analyze/", views_saas_analyze.analyze_with_usage, name="sinaplint_saas_analyze"),
    path("dashboard/summary/", views_dashboard.DashboardSummaryView.as_view(), name="sinaplint_dashboard_summary"),
    path("dashboard/history/", views_dashboard.DashboardHistoryView.as_view(), name="sinaplint_dashboard_history"),
    path("dashboard/billing/", views_dashboard.DashboardBillingView.as_view(), name="sinaplint_dashboard_billing"),
    path("dashboard/overview/", views_dashboard.DashboardOverviewView.as_view(), name="sinaplint_dashboard_overview"),
]
