from __future__ import annotations

from django.db import models


class PricingLog(models.Model):
    """Auditoria de chamadas a /agno/pricing/ (explicabilidade no Admin)."""

    empresa_id = models.IntegerField(null=True, blank=True, db_index=True)
    produto_id = models.IntegerField(db_index=True)

    preco_base = models.DecimalField(max_digits=12, decimal_places=2)
    preco_final = models.DecimalField(max_digits=12, decimal_places=2)
    fator_total = models.DecimalField(max_digits=10, decimal_places=4)

    fatores = models.JSONField(default=dict)
    canal = models.CharField(max_length=50, default="app")
    motivo = models.TextField(blank=True)

    timestamp = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        ordering = ["-timestamp"]
        verbose_name = "Log de precificação (Agno)"
        verbose_name_plural = "Logs de precificação (Agno)"
        indexes = [
            models.Index(fields=["empresa_id", "-timestamp"]),
            models.Index(fields=["produto_id", "-timestamp"]),
        ]

    def __str__(self) -> str:
        return f"PricingLog pk={self.pk} produto={self.produto_id} final={self.preco_final}"
