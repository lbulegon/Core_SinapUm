"""
Planos (Stripe) e assinatura por utilizador Django.
"""

from __future__ import annotations

from django.conf import settings
from django.db import models


class Plan(models.Model):
    """Plano comercial (Free / Pro / Scale)."""

    name = models.CharField(max_length=50)
    slug = models.SlugField(max_length=32, unique=True, db_index=True)
    stripe_price_id = models.CharField(
        max_length=100,
        blank=True,
        help_text="Stripe Price ID (vazio para Free)",
    )
    max_analyses_per_month = models.IntegerField(
        help_text="Limite mensal de análises; -1 = ilimitado",
    )
    max_repos = models.PositiveIntegerField(
        default=5,
        help_text="Máximo de repositórios registados por utilizador",
    )
    is_public = models.BooleanField(
        default=True,
        help_text="Mostrar na UI de upgrade",
    )
    sort_order = models.PositiveSmallIntegerField(default=0)

    class Meta:
        ordering = ("sort_order", "id")

    def __str__(self) -> str:
        return f"{self.name} ({self.slug})"


class Subscription(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="sinaplint_subscription",
    )
    stripe_customer_id = models.CharField(max_length=120, blank=True, db_index=True)
    stripe_subscription_id = models.CharField(max_length=120, blank=True, db_index=True)
    plan = models.ForeignKey(
        Plan,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="subscriptions",
    )
    status = models.CharField(
        max_length=50,
        default="active",
        help_text="active, canceled, past_due, trialing, incomplete, …",
    )
    current_period_end = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Assinatura SinapLint"
        verbose_name_plural = "Assinaturas SinapLint"

    def __str__(self) -> str:
        return f"{self.user_id} → {self.plan_id}"
