"""
TaskManager — cria tarefas, atualiza status, dispara execução via Celery.

Não altera fluxos legados.
"""
import logging
import uuid
from typing import Any, Dict, Optional

from django.utils import timezone

from .models import AgentTask
from .state_store import StateStore

logger = logging.getLogger(__name__)


class TaskManager:
    """Gerencia ciclo de vida de AgentTask e enfileira execução."""

    def __init__(self, state_store: Optional[StateStore] = None):
        self.state_store = state_store or StateStore()

    def create_task(
        self,
        agent_name: str,
        payload: Dict[str, Any],
        *,
        trace_id: Optional[str] = None,
        max_retries: int = 3,
        timeout_seconds: Optional[int] = None,
        idempotency_key: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Cria uma AgentTask (PENDING) e opcionalmente enfileira execução.
        Retorna { "task_id": "...", "status": "PENDING", ... }.
        """
        if idempotency_key:
            existing = AgentTask.objects.filter(idempotency_key=idempotency_key).first()
            if existing:
                return {
                    "task_id": str(existing.task_id),
                    "status": existing.status,
                    "created_at": existing.created_at.isoformat(),
                    "idempotency_reused": True,
                }
        task = AgentTask.objects.create(
            agent_name=agent_name,
            status=AgentTask.Status.PENDING,
            payload=payload,
            trace_id=trace_id,
            max_retries=max_retries,
            timeout_seconds=timeout_seconds,
            idempotency_key=idempotency_key,
        )
        # Enfileirar execução (Celery)
        try:
            from .tasks import run_acp_task
            run_acp_task.delay(str(task.task_id))
        except Exception as e:
            logger.warning("Celery enqueue failed (task created): %s", e)
        return {
            "task_id": str(task.task_id),
            "status": task.status,
            "created_at": task.created_at.isoformat(),
        }

    def get_task(self, task_id: str) -> Optional[Dict[str, Any]]:
        """Retorna estado da tarefa."""
        return self.state_store.get(task_id)

    def cancel_task(self, task_id: str) -> bool:
        """Marca tarefa como CANCELLED se ainda PENDING ou WAITING."""
        try:
            task = AgentTask.objects.get(task_id=task_id)
            if task.status in (AgentTask.Status.PENDING, AgentTask.Status.WAITING):
                task.status = AgentTask.Status.CANCELLED
                task.finished_at = timezone.now()
                task.save(update_fields=["status", "finished_at", "updated_at"])
                return True
            return False
        except AgentTask.DoesNotExist:
            return False
