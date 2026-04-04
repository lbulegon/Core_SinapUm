"""Rotas SinapLint SaaS (billing, webhook, análise com limite, dashboard)."""

from django.urls import path

from app_sinaplint import views_billing, views_dashboard, views_saas_analyze
from app_sinaplint.views_stripe_webhook import StripeWebhookView

urlpatterns = [
    path("billing/checkout/", views_billing.CreateCheckoutSessionView.as_view(), name="sinaplint_checkout"),
    path("billing/plans/", views_billing.PlansListView.as_view(), name="sinaplint_plans"),
    path("webhooks/stripe/", StripeWebhookView.as_view(), name="sinaplint_stripe_webhook"),
    path("v1/analyze/", views_saas_analyze.analyze_with_usage, name="sinaplint_saas_analyze"),
    path("dashboard/summary/", views_dashboard.DashboardSummaryView.as_view(), name="sinaplint_dashboard_summary"),
    path("dashboard/history/", views_dashboard.DashboardHistoryView.as_view(), name="sinaplint_dashboard_history"),
    path("dashboard/billing/", views_dashboard.DashboardBillingView.as_view(), name="sinaplint_dashboard_billing"),
    path("dashboard/overview/", views_dashboard.DashboardOverviewView.as_view(), name="sinaplint_dashboard_overview"),
]
