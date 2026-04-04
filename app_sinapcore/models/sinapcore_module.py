from __future__ import annotations

from django.db import models


class SinapCoreModule(models.Model):
    """Configuração persistida dos módulos SinapCore (Admin — sem alterar código)."""

    MODULE_CHOICES = [
        ("environmental", "Environmental"),
        ("cognitive", "Cognitive"),
        ("emotional", "Emotional"),
        ("semiotic", "Semiotic"),
        ("csv", "CSV"),
    ]

    name = models.CharField(max_length=50, choices=MODULE_CHOICES, unique=True)
    enabled = models.BooleanField(default=True)
    priority = models.IntegerField(default=1)
    config = models.JSONField(blank=True, null=True, help_text="Parâmetros opcionais por módulo (JSON).")
    description = models.TextField(blank=True, help_text="Documentação interna do módulo.")
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ("priority", "name")
        verbose_name = "Módulo SinapCore"
        verbose_name_plural = "Módulos SinapCore"

    def __str__(self) -> str:
        return f"{self.name} (enabled={self.enabled})"
