from __future__ import annotations

from django.db import models


class AgnoDecisionLog(models.Model):
    """Registro estruturado de decisoes do Chef Agno (auditoria/explicabilidade)."""

    module = models.CharField(max_length=40, db_index=True)
    action = models.CharField(max_length=80, db_index=True)
    product_id = models.IntegerField(null=True, blank=True, db_index=True)
    product_name = models.CharField(max_length=120, blank=True)
    reason = models.CharField(max_length=255)
    payload = models.JSONField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        ordering = ("-created_at",)
        verbose_name = "Log de decisao Agno"
        verbose_name_plural = "Logs de decisao Agno"

    def __str__(self) -> str:
        produto = self.product_name or self.product_id or "n/a"
        return f"{self.module}:{self.action}:{produto}"
