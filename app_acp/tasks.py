"""
Celery tasks ACP — execução assíncrona de AgentTask.

Integra com core.services.task_queue_service (broker Redis).
"""
import logging
from celery import shared_task

logger = logging.getLogger(__name__)


@shared_task(bind=True, autoretry_for=(Exception,), retry_backoff=True, retry_kwargs={"max_retries": 3})
def run_acp_task(self, task_id: str) -> str:
    """
    Executa uma AgentTask por task_id.
    Chama ExecutionEngine.run_task e atualiza estado no Postgres.
    """
    from .execution_engine import ExecutionEngine
    engine = ExecutionEngine()
    result = engine.run_task(task_id)
    logger.info("ACP task %s finished: ok=%s", task_id, result.get("ok"))
    return task_id
