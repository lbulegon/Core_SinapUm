from __future__ import annotations

from django.db import models


class SinapCoreLog(models.Model):
    """Auditoria de decisões do SinapEngine (resposta por módulo)."""

    module = models.CharField(max_length=50, db_index=True)
    decision = models.CharField(max_length=100)
    action = models.CharField(max_length=100, null=True, blank=True)
    context = models.JSONField(null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        ordering = ("-timestamp",)
        verbose_name = "Log SinapCore"
        verbose_name_plural = "Logs SinapCore"

    def __str__(self) -> str:
        return f"{self.module} - {self.decision}"
