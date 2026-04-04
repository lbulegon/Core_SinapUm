"""
Limites de repositórios por plano.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from app_sinaplint.models_repository import Repository
from app_sinaplint.services.usage_limits import get_effective_plan

if TYPE_CHECKING:
    from django.contrib.auth.models import AbstractUser


class RepoLimitExceeded(Exception):
    def __init__(self, message: str, *, limit: int, used: int) -> None:
        self.limit = limit
        self.used = used
        super().__init__(message)


def ensure_repository_for_user(
    user: AbstractUser,
    url: str,
    *,
    name: str | None = None,
    provider: str = "github",
) -> Repository:
    """
    Obtém ou cria :class:`~app_sinaplint.models_repository.Repository` respeitando ``max_repos`` do plano.
    """
    plan = get_effective_plan(user)
    if plan is None:
        raise RepoLimitExceeded("Sem plano.", limit=0, used=0)

    existing = Repository.objects.filter(user=user, url=url).first()
    if existing:
        return existing

    limit = int(plan.max_repos or 0)
    used = Repository.objects.filter(user=user).count()
    if limit > 0 and used >= limit:
        raise RepoLimitExceeded(
            f"Limite de repositórios atingido ({limit}).",
            limit=limit,
            used=used,
        )

    return Repository.objects.create(
        user=user,
        url=url,
        name=(name or url)[:255],
        provider=provider[:50],
    )
