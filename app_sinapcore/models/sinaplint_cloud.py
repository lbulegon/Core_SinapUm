"""
SinapLint Cloud — multi-tenant mínimo (API key + projetos + histórico de análises).

Ative migrações e proteja o endpoint em produção (HTTPS, rate limit, rotação de keys).
"""

from __future__ import annotations

import secrets

from django.db import models


def _generate_api_key() -> str:
    return f"sl_{secrets.token_urlsafe(32)}"


class SinapLintTenant(models.Model):
    """Organização / cliente SaaS."""

    name = models.CharField(max_length=120)
    api_key = models.CharField(max_length=128, unique=True, db_index=True, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Tenant SinapLint"
        verbose_name_plural = "Tenants SinapLint"

    def save(self, *args, **kwargs) -> None:
        if not self.api_key:
            self.api_key = _generate_api_key()
        super().save(*args, **kwargs)

    def __str__(self) -> str:
        return self.name


class SinapLintProject(models.Model):
    """Repositório ou produto analisado dentro do tenant."""

    tenant = models.ForeignKey(
        SinapLintTenant,
        on_delete=models.CASCADE,
        related_name="sinaplint_projects",
    )
    name = models.CharField(max_length=120)
    repo_url = models.URLField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Projeto SinapLint"
        verbose_name_plural = "Projetos SinapLint"
        unique_together = [["tenant", "name"]]

    def __str__(self) -> str:
        return f"{self.tenant.name} / {self.name}"


class SinapLintAnalysis(models.Model):
    """Resultado persistido de `SinapLint().run()`."""

    project = models.ForeignKey(
        SinapLintProject,
        on_delete=models.CASCADE,
        related_name="analyses",
    )
    score = models.PositiveSmallIntegerField()
    result = models.JSONField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ("-created_at",)
        verbose_name = "Análise SinapLint"
        verbose_name_plural = "Análises SinapLint"

    def __str__(self) -> str:
        return f"{self.project_id} @ {self.score}"
