"""
Contagem mensal de análises por utilizador.
"""

from __future__ import annotations

from django.conf import settings
from django.db import models


class Usage(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="sinaplint_usage_months",
    )
    month = models.DateField(
        help_text="Primeiro dia do mês (UTC)",
        db_index=True,
    )
    analyses_count = models.PositiveIntegerField(default=0)

    class Meta:
        verbose_name = "Uso mensal SinapLint"
        verbose_name_plural = "Usos mensais SinapLint"
        constraints = [
            models.UniqueConstraint(fields=["user", "month"], name="uniq_sinaplint_usage_user_month"),
        ]

    def __str__(self) -> str:
        return f"{self.user_id} {self.month} → {self.analyses_count}"
