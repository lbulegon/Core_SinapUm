from __future__ import annotations

from django.db import models


class SinapCoreCommand(models.Model):
    """Fila de comandos operacionais (EOC → CommandExecutor → efeitos no domínio)."""

    COMMAND_TYPES = [
        ("reduce_load", "Reduzir carga"),
        ("pause_orders", "Pausar pedidos"),
        ("normalize", "Normalizar operação"),
    ]

    STATUS_CHOICES = [
        ("pending", "Pendente"),
        ("running", "Em execução"),
        ("done", "Concluído"),
        ("failed", "Falhou"),
    ]

    status = models.CharField(max_length=20, default="pending", choices=STATUS_CHOICES)
    command = models.CharField(max_length=50, choices=COMMAND_TYPES)
    payload = models.JSONField(null=True, blank=True)
    executed = models.BooleanField(default=False)
    source = models.CharField(
        max_length=20,
        default="manual",
        help_text="manual | auto (EOC)",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ("-created_at",)
        verbose_name = "Comando SinapCore"
        verbose_name_plural = "Comandos SinapCore"

    def __str__(self) -> str:
        return f"{self.command} - {self.status}"
