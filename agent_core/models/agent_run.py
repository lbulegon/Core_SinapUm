from __future__ import annotations

import uuid

from django.db import models


class AgentRun(models.Model):
    """
    Estado persistido de uma execução cognitiva — trilha única de auditoria.

    `historico` armazena entradas estruturadas por fase (plan, act, observe, reflect).
    """

    class Status(models.TextChoices):
        RUNNING = "running", "Running"
        AWAITING_HUMAN = "awaiting_human", "Awaiting human"
        COMPLETED = "completed", "Completed"
        FAILED = "failed", "Failed"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    objetivo = models.TextField()
    estado_atual = models.JSONField(default=dict, blank=True)
    plano = models.JSONField(default=dict, blank=True)
    iteracao = models.PositiveIntegerField(default=0)
    historico = models.JSONField(default=list, blank=True)
    status = models.CharField(
        max_length=32,
        choices=Status.choices,
        default=Status.RUNNING,
        db_index=True,
    )
    error_message = models.TextField(blank=True, default="")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        app_label = "agent_core"
        ordering = ("-created_at",)
        verbose_name = "Agent run"
        verbose_name_plural = "Agent runs"

    def __str__(self) -> str:
        return f"{self.id} ({self.status})"
