"""
Modelos de billing partilhados entre SaaS (SinapLint, Eventix, MotoPro, …).

Cada produto tem catálogo de planos; cada utilizador tem no máximo uma
assinatura Stripe ativa por produto (customer/subscription por par user+product).
"""

from __future__ import annotations

from django.conf import settings
from django.db import models


class SaaSProduct(models.Model):
    """Registo lógico de um produto (app) que fatura via Core."""

    slug = models.SlugField(max_length=64, unique=True, db_index=True)
    display_name = models.CharField(max_length=120)
    is_active = models.BooleanField(default=True)
    notes = models.TextField(blank=True, help_text="Interno: URL docs, contacto comercial, …")

    class Meta:
        ordering = ("slug",)
        verbose_name = "Produto SaaS"
        verbose_name_plural = "Produtos SaaS"

    def __str__(self) -> str:
        return self.display_name


class CatalogPlan(models.Model):
    """Plano comercial por produto (alinhado a um Price ID Stripe, opcional)."""

    product = models.ForeignKey(
        SaaSProduct,
        on_delete=models.CASCADE,
        related_name="plans",
    )
    name = models.CharField(max_length=80)
    slug = models.SlugField(max_length=64)
    stripe_price_id = models.CharField(
        max_length=120,
        blank=True,
        db_index=True,
        help_text="Stripe Price ID; vazio = plano gratuito / só limites internos",
    )
    limits = models.JSONField(
        default=dict,
        blank=True,
        help_text="Limites por app, ex.: {\"max_analyses_per_month\": 100, \"max_repos\": 5}",
    )
    is_public = models.BooleanField(
        default=True,
        help_text="Listado em GET /plans/ para landing / upgrade",
    )
    sort_order = models.PositiveSmallIntegerField(default=0)

    class Meta:
        ordering = ("product", "sort_order", "id")
        verbose_name = "Plano (catálogo / Stripe)"
        verbose_name_plural = "Planos (catálogo / Stripe)"
        constraints = [
            models.UniqueConstraint(
                fields=("product", "slug"),
                name="platform_billing_unique_plan_slug_per_product",
            ),
        ]

    def __str__(self) -> str:
        return f"{self.product.slug}:{self.slug}"


class PlatformSubscription(models.Model):
    """Estado de faturação Stripe por (utilizador, produto)."""

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="platform_subscriptions",
    )
    product = models.ForeignKey(
        SaaSProduct,
        on_delete=models.CASCADE,
        related_name="subscriptions",
    )
    plan = models.ForeignKey(
        CatalogPlan,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="active_subscriptions",
    )
    stripe_customer_id = models.CharField(max_length=120, blank=True, db_index=True)
    stripe_subscription_id = models.CharField(max_length=120, blank=True, db_index=True)
    status = models.CharField(
        max_length=50,
        default="none",
        help_text="none, active, canceled, past_due, trialing, incomplete, …",
    )
    current_period_end = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=("user", "product"),
                name="platform_billing_unique_user_product",
            ),
        ]
        verbose_name = "Assinatura plataforma"
        verbose_name_plural = "Assinaturas plataforma"

    def __str__(self) -> str:
        return f"{self.user_id} @ {self.product.slug}"
