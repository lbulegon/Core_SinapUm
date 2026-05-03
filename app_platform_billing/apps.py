from django.apps import AppConfig


class AppPlatformBillingConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "app_platform_billing"
    # Nome no índice do Admin (Ctrl+F: "SaaS" ou "billing")
    verbose_name = "SaaS / Billing (Stripe)"

    def ready(self) -> None:
        # Garante que os modelos aparecem no Admin após o arranque (deploy / ordem de apps).
        import app_platform_billing.admin  # noqa: F401
