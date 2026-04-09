"""
ExecutorAgent — executa plano via ACP (AgentTask) ou step-by-step via /mcp/call.
Saída: results + trace_id + status. Idempotente quando idempotency_key fornecido.
"""
import logging
import uuid
from typing import Any, Dict, Optional

from .schemas import A2APlan

logger = logging.getLogger(__name__)


class ExecutorAgent:
    """
    Executa um A2APlan: preferencialmente cria AgentTask ACP e dispara run_acp_task;
    alternativamente executa step-by-step chamando /mcp/call (modo síncrono).
    """

    def __init__(self, use_acp: bool = True):
        self.use_acp = use_acp

    def execute(
        self,
        plan: A2APlan,
        context: Optional[Dict[str, Any]] = None,
        trace_id: Optional[str] = None,
        idempotency_key: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Executa o plano. Se use_acp=True, cria AgentTask e retorna task_id + trace_id.
        Se use_acp=False, executa steps via /mcp/call e retorna result síncrono.
        """
        context = context or {}
        trace_id = trace_id or str(uuid.uuid4())
        payload = plan.to_acp_payload()

        if self.use_acp:
            return self._execute_via_acp(
                payload=payload,
                trace_id=trace_id,
                idempotency_key=idempotency_key,
            )
        return self._execute_sync(plan, trace_id)

    def _execute_via_acp(
        self,
        payload: Dict[str, Any],
        trace_id: str,
        idempotency_key: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Cria AgentTask e enfileira; retorna task_id e trace_id."""
        from app_acp.task_manager import TaskManager
        manager = TaskManager()
        result = manager.create_task(
            agent_name="a2a_executor",
            payload=payload,
            trace_id=trace_id,
            max_retries=3,
            timeout_seconds=120,
            idempotency_key=idempotency_key,
        )
        task_id = result.get("task_id")
        return {
            "trace_id": trace_id,
            "task_id": task_id,
            "status": result.get("status", "PENDING"),
            "result": None,
        }

    def _execute_sync(self, plan: A2APlan, trace_id: str) -> Dict[str, Any]:
        """Executa steps chamando /mcp/call (síncrono). MVP: apenas primeiro step."""
        import os
        import requests
        mcp_url = (os.environ.get("MCP_SERVICE_URL") or "http://mcp_service:7010").rstrip("/") + "/mcp/call"
        results = []
        for i, step in enumerate(plan.steps):
            payload = {
                "tool": step.tool_name,
                "version": step.tool_version or "1.0",
                "input": step.args,
                "context_pack": {"meta": {"trace_id": trace_id}},
            }
            try:
                r = requests.post(
                    mcp_url,
                    json=payload,
                    headers={"Content-Type": "application/json"},
                    timeout=step.timeout_seconds or 60,
                )
                data = r.json() if r.content else {}
                results.append(data)
                if not data.get("ok"):
                    return {
                        "trace_id": trace_id,
                        "task_id": None,
                        "status": "FAILED",
                        "result": None,
                        "steps_result": results,
                        "error": data.get("error"),
                    }
            except Exception as e:
                logger.exception("ExecutorAgent sync step failed")
                return {
                    "trace_id": trace_id,
                    "task_id": None,
                    "status": "FAILED",
                    "result": None,
                    "steps_result": results,
                    "error": str(e),
                }
        return {
            "trace_id": trace_id,
            "task_id": None,
            "status": "COMPLETED",
            "result": results[-1].get("output") if results else None,
            "steps_result": results,
        }
