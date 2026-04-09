"""
StateStore — fonte de verdade em Postgres (AgentTask); cache opcional em Redis.

Não altera comportamento de outros módulos.
"""
import logging
from typing import Any, Dict, Optional

from django.utils import timezone

from .models import AgentTask

logger = logging.getLogger(__name__)


class StateStore:
    """Persistência de estado de tarefas ACP (Postgres)."""

    def get(self, task_id: str) -> Optional[Dict[str, Any]]:
        """Retorna tarefa por task_id (UUID string)."""
        try:
            task = AgentTask.objects.get(task_id=task_id)
            return self._task_to_dict(task)
        except AgentTask.DoesNotExist:
            return None

    def set_status(
        self,
        task_id: str,
        status: str,
        result=None,
        error=None,
        started_at=None,
        finished_at=None,
    ) -> bool:
        """Atualiza status (e opcionalmente result/error/started_at/finished_at)."""
        try:
            task = AgentTask.objects.get(task_id=task_id)
            task.status = status
            if result is not None:
                task.result = result
            if error is not None:
                task.error = error[:5000] if error else None
            if started_at is not None:
                task.started_at = started_at
            if finished_at is not None:
                task.finished_at = finished_at
            task.save(update_fields=["status", "result", "error", "started_at", "finished_at", "updated_at"])
            return True
        except AgentTask.DoesNotExist:
            logger.warning("AgentTask %s not found for set_status", task_id)
            return False

    def increment_retry(self, task_id: str) -> bool:
        """Incrementa retry_count."""
        try:
            task = AgentTask.objects.select_for_update().get(task_id=task_id)
            task.retry_count += 1
            task.save(update_fields=["retry_count", "updated_at"])
            return True
        except AgentTask.DoesNotExist:
            return False

    @staticmethod
    def _task_to_dict(task: AgentTask) -> Dict[str, Any]:
        return {
            "task_id": str(task.task_id),
            "agent_name": task.agent_name,
            "status": task.status,
            "payload": task.payload,
            "result": task.result,
            "error": task.error,
            "trace_id": task.trace_id,
            "retry_count": task.retry_count,
            "max_retries": task.max_retries,
            "timeout_seconds": task.timeout_seconds,
            "idempotency_key": task.idempotency_key,
            "created_at": task.created_at.isoformat() if task.created_at else None,
            "updated_at": task.updated_at.isoformat() if task.updated_at else None,
            "started_at": task.started_at.isoformat() if task.started_at else None,
            "finished_at": task.finished_at.isoformat() if task.finished_at else None,
        }
