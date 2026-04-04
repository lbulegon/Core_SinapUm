"""
Repositórios registados, histórico de análises e delta persistido.
"""

from __future__ import annotations

from django.conf import settings
from django.db import models


class Repository(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="sinaplint_repositories",
    )
    name = models.CharField(max_length=255)
    url = models.URLField(max_length=500)
    provider = models.CharField(max_length=50, default="github")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Repositório SinapLint"
        verbose_name_plural = "Repositórios SinapLint"
        constraints = [
            models.UniqueConstraint(fields=["user", "url"], name="uniq_sinaplint_repo_user_url"),
        ]

    def __str__(self) -> str:
        return f"{self.name}"


class Analysis(models.Model):
    repository = models.ForeignKey(
        Repository,
        on_delete=models.CASCADE,
        related_name="analyses",
    )
    commit_hash = models.CharField(max_length=100, null=True, blank=True)
    branch = models.CharField(max_length=100, null=True, blank=True)
    score = models.IntegerField()
    architecture_score = models.IntegerField(null=True, blank=True)
    result = models.JSONField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ("-created_at",)
        verbose_name = "Análise SinapLint"
        verbose_name_plural = "Análises SinapLint"

    def __str__(self) -> str:
        return f"{self.repository_id} @ {self.score}"


class AnalysisDelta(models.Model):
    analysis = models.OneToOneField(
        Analysis,
        on_delete=models.CASCADE,
        related_name="delta",
    )
    score_change = models.IntegerField(default=0)
    new_cycles = models.IntegerField(default=0)
    coupling_increased = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Delta de análise"
        verbose_name_plural = "Deltas de análise"

    def __str__(self) -> str:
        return f"Δ {self.analysis_id}"
