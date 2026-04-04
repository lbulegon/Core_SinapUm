"""
Limites mensais de análise por plano.
"""

from __future__ import annotations

from datetime import date
from typing import TYPE_CHECKING

from django.db import transaction
from django.utils import timezone

if TYPE_CHECKING:
    from django.contrib.auth.models import AbstractUser

from app_sinaplint.models_billing import Plan, Subscription
from app_sinaplint.models_usage import Usage


class UsageLimitExceeded(Exception):
    """Limite de análises mensais atingido."""

    def __init__(self, message: str, *, limit: int, used: int) -> None:
        self.limit = limit
        self.used = used
        super().__init__(message)


def _month_start(d: date | None = None) -> date:
    if d is None:
        d = timezone.now().date()
    return date(d.year, d.month, 1)


def get_effective_plan(user: AbstractUser) -> Plan | None:
    """Plano ativo ou Free (slug ``free``)."""
    if not getattr(user, "is_authenticated", False):
        return None
    try:
        sub: Subscription = user.sinaplint_subscription
    except Subscription.DoesNotExist:
        sub = None
    if sub and sub.status in ("active", "trialing") and sub.plan_id:
        return sub.plan
    return Plan.objects.filter(slug="free").first()


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

    limit = plan.max_analyses_per_month
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
    limit = plan.max_analyses_per_month
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
