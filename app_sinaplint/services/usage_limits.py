"""
Limites mensais de análise por plano (catálogo plataforma ``CatalogPlan``).
"""

from __future__ import annotations

from datetime import date
from typing import TYPE_CHECKING

from django.db import transaction
from django.utils import timezone

if TYPE_CHECKING:
    from django.contrib.auth.models import AbstractUser

from app_platform_billing.catalog_limits import (
    analyses_monthly_limit,
    get_free_catalog_plan,
    get_platform_subscription,
    get_saas_product,
    repos_limit,
    SINAPLINT_PRODUCT_SLUG,
)
from app_platform_billing.models import CatalogPlan
from app_sinaplint.models_usage import Usage


class UsageLimitExceeded(Exception):
    """Limite mensal de análises atingido."""

    def __init__(self, message: str, *, limit: int, used: int) -> None:
        self.limit = limit
        self.used = used
        super().__init__(message)


def _month_start(d: date | None = None) -> date:
    if d is None:
        d = timezone.now().date()
    return date(d.year, d.month, 1)


def get_effective_plan(user: AbstractUser) -> CatalogPlan | None:
    """Plano ativo (assinatura Stripe) ou plano Free do catálogo SinapLint."""
    if not getattr(user, "is_authenticated", False):
        return None
    prod = get_saas_product(SINAPLINT_PRODUCT_SLUG)
    if not prod:
        return None
    ps = get_platform_subscription(user.pk, SINAPLINT_PRODUCT_SLUG)
    if ps and ps.status in ("active", "trialing") and ps.plan_id:
        return ps.plan
    return get_free_catalog_plan(prod)


@transaction.atomic
def check_and_increment_usage(user: AbstractUser) -> Usage:
    """
    Garante que o utilizador não excedeu o limite do plano e incrementa o contador.

    :raises UsageLimitExceeded: se o limite for atingido (não incrementa).
    """
    plan = get_effective_plan(user)
    if plan is None:
        raise UsageLimitExceeded(
            "Sem plano associado (crie conta ou contacte suporte).",
            limit=0,
            used=0,
        )

    limit = analyses_monthly_limit(plan)
    m = _month_start()
    usage, _ = Usage.objects.select_for_update().get_or_create(
        user=user,
        month=m,
        defaults={"analyses_count": 0},
    )

    if limit < 0:
        usage.analyses_count += 1
        usage.save(update_fields=["analyses_count"])
        return usage

    if usage.analyses_count >= limit:
        raise UsageLimitExceeded(
            f"Limite mensal atingido ({limit} análises).",
            limit=limit,
            used=usage.analyses_count,
        )

    usage.analyses_count += 1
    usage.save(update_fields=["analyses_count"])
    return usage


def check_limit(user: AbstractUser) -> None:
    """
    Alias só de verificação (sem incrementar). Útil para pré-cheques.
    """
    plan = get_effective_plan(user)
    if plan is None:
        raise UsageLimitExceeded(
            "Sem plano associado.",
            limit=0,
            used=0,
        )
    limit = analyses_monthly_limit(plan)
    if limit < 0:
        return
    m = _month_start()
    usage = Usage.objects.filter(user=user, month=m).first()
    used = int(usage.analyses_count) if usage else 0
    if used >= limit:
        raise UsageLimitExceeded(
            f"Limite mensal atingido ({limit} análises).",
            limit=limit,
            used=used,
        )
