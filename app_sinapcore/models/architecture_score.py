from __future__ import annotations

from django.db import models


class ArchitectureScore(models.Model):
    """Histórico de scores do validador arquitetural (governança / tendência)."""

    score = models.PositiveSmallIntegerField(db_index=True)
    quality = models.CharField(max_length=24, db_index=True)
    passed = models.BooleanField(default=False, db_index=True)
    min_pass_score = models.PositiveSmallIntegerField(default=80)
    details = models.JSONField(null=True, blank=True)
    source = models.CharField(
        max_length=64,
        default="validate_framework",
        help_text="Origem da execução (ex.: validate_framework, shell).",
    )
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        ordering = ("-created_at",)
        verbose_name = "Score arquitetural"
        verbose_name_plural = "Scores arquiteturais"

    def __str__(self) -> str:
        return f"{self.score}/100 ({self.quality}) @ {self.created_at.isoformat()}"
