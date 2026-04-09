"""
Modelo AgentTask — estado persistente de tarefas de agente (ACP).

Não altera nenhum modelo existente; apenas aditivo.
"""
import uuid
from django.db import models


class AgentTask(models.Model):
    """Tarefa de execução de agente (ACP)."""

    class Status(models.TextChoices):
        PENDING = "PENDING", "Pendente"
        RUNNING = "RUNNING", "Em execução"
        WAITING = "WAITING", "Aguardando"
        FAILED = "FAILED", "Falhou"
        COMPLETED = "COMPLETED", "Concluída"
        CANCELLED = "CANCELLED", "Cancelada"

    task_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True, db_index=True)
    agent_name = models.CharField(max_length=120)
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING,
        db_index=True,
    )
    payload = models.JSONField(default=dict)
    result = models.JSONField(null=True, blank=True)
    error = models.TextField(null=True, blank=True)
    trace_id = models.CharField(max_length=64, null=True, blank=True, db_index=True)

    retry_count = models.PositiveIntegerField(default=0)
    max_retries = models.PositiveIntegerField(default=3)
    timeout_seconds = models.PositiveIntegerField(null=True, blank=True)
    idempotency_key = models.CharField(max_length=255, null=True, blank=True, db_index=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    started_at = models.DateTimeField(null=True, blank=True)
    finished_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = "acp_agent_task"
        verbose_name = "Agent Task"
        verbose_name_plural = "Agent Tasks"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["status"]),
            models.Index(fields=["agent_name", "status"]),
            models.Index(fields=["created_at"]),
        ]

    def __str__(self):
        return f"{self.agent_name} [{self.status}] {self.task_id}"
