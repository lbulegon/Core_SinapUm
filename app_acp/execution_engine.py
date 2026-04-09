"""
ExecutionEngine — executa passos chamando MCP (POST /mcp/call), aplica timeout e retry.

Não altera fluxos legados; apenas execução ACP.
"""
import logging
import os
import time
import uuid
from typing import Any, Dict, Optional

import requests
from django.utils import timezone

from .models import AgentTask
from .state_store import StateStore

logger = logging.getLogger(__name__)

# URL do MCP Service (FastAPI gateway em 7010). Core Django não expõe /mcp/call; usar mcp_service.
MCP_SERVICE_URL = (os.environ.get("MCP_SERVICE_URL") or os.environ.get("MCP_CALL_URL") or "http://mcp_service:7010").rstrip("/")
MCP_CALL_URL = MCP_SERVICE_URL + "/mcp/call"
DEFAULT_TIMEOUT = int(os.environ.get("ACP_MCP_TIMEOUT", "120"))
DEFAULT_MAX_RETRIES = 3


def call_mcp_tool(
    tool: str,
    version: Optional[str],
    input_data: Dict[str, Any],
    *,
    trace_id: Optional[str] = None,
    timeout_seconds: int = DEFAULT_TIMEOUT,
) -> Dict[str, Any]:
    """
    Chama uma tool MCP via POST /mcp/call.
    Retorna dict com ok, output, error, latency_ms, request_id, trace_id.
    """
    payload = {"tool": tool, "input": input_data}
    if version:
        payload["version"] = version
    if trace_id:
        payload["context_pack"] = {"meta": {"trace_id": trace_id, "request_id": str(uuid.uuid4())}}
    headers = {"Content-Type": "application/json"}
    api_key = os.environ.get("INTERNAL_API_TOKEN") or os.environ.get("SINAPUM_API_KEY")
    if api_key:
        headers["X-SINAPUM-KEY"] = api_key
    try:
        r = requests.post(MCP_CALL_URL, json=payload, headers=headers, timeout=timeout_seconds)
        data = r.json() if r.content else {}
        data.setdefault("ok", r.status_code == 200)
        data.setdefault("status_code", r.status_code)
        return data
    except requests.exceptions.Timeout:
        return {"ok": False, "error": "timeout", "status_code": 408}
    except Exception as e:
        logger.exception("MCP call failed %s", tool)
        return {"ok": False, "error": str(e), "status_code": 500}


class ExecutionEngine:
    """Executa uma AgentTask chamando MCP e atualiza estado."""

    def __init__(self, state_store: Optional[StateStore] = None):
        self.state_store = state_store or StateStore()

    def run_task(self, task_id: str) -> Dict[str, Any]:
        """
        Executa a tarefa: lê payload (steps ou tool única), chama MCP, grava result/error.
        Retorna dict final (result ou error).
        """
        state = self.state_store.get(task_id)
        if not state:
            return {"ok": False, "error": "task_not_found"}
        if state["status"] not in (AgentTask.Status.PENDING, AgentTask.Status.WAITING):
            return {"ok": True, "status": state["status"], "result": state.get("result")}

        payload = state.get("payload") or {}
        trace_id = state.get("trace_id") or str(uuid.uuid4())
        timeout_seconds = state.get("timeout_seconds") or DEFAULT_TIMEOUT
        max_retries = state.get("max_retries") or DEFAULT_MAX_RETRIES
        retry_count = state.get("retry_count") or 0

        # Fase 2: decisão cognitiva pré-computada (prioridade / ação / risco)
        decision_output = payload.get("decision_output") or payload.get("decision")
        if isinstance(decision_output, dict):
            logger.info(
                "ExecutionEngine task=%s cognitive_action=%s confidence=%s risk=%s",
                task_id,
                decision_output.get("action"),
                decision_output.get("confidence"),
                decision_output.get("risk_level"),
            )
            if decision_output.get("risk_level") == "high":
                timeout_seconds = min(int(timeout_seconds) + 30, 600)

        # Marcar RUNNING
        self.state_store.set_status(
            task_id,
            AgentTask.Status.RUNNING,
            started_at=timezone.now(),
        )

        # Payload pode ser: { "tool": "...", "version": "...", "input": {...} } ou { "steps": [...] }
        tool = payload.get("tool")
        steps = payload.get("steps")
        if steps:
            results = []
            for i, step in enumerate(steps):
                step_tool = step.get("tool") or tool
                step_version = step.get("version") or payload.get("version")
                step_input = step.get("input", {})
                step_timeout = step.get("timeout_seconds") or timeout_seconds
                if not step_tool:
                    self.state_store.set_status(
                        task_id,
                        AgentTask.Status.FAILED,
                        error=f"step {i} missing tool",
                        finished_at=timezone.now(),
                    )
                    return {"ok": False, "error": "step missing tool"}
                out = call_mcp_tool(
                    step_tool,
                    step_version,
                    step_input,
                    trace_id=trace_id,
                    timeout_seconds=step_timeout,
                )
                results.append(out)
                if not out.get("ok"):
                    self.state_store.set_status(
                        task_id,
                        AgentTask.Status.FAILED,
                        result={"steps": results},
                        error=out.get("error", "mcp_call_failed"),
                        finished_at=timezone.now(),
                    )
                    return {"ok": False, "error": out.get("error"), "steps": results}
            self.state_store.set_status(
                task_id,
                AgentTask.Status.COMPLETED,
                result={"steps": results, "output": results[-1].get("output") if results else None},
                finished_at=timezone.now(),
            )
            return {"ok": True, "result": results[-1].get("output") if results else None, "steps": results}
        else:
            # Chamada única
            tool = payload.get("tool")
            version = payload.get("version")
            input_data = payload.get("input", {})
            if not tool:
                self.state_store.set_status(
                    task_id,
                    AgentTask.Status.FAILED,
                    error="payload missing tool",
                    finished_at=timezone.now(),
                )
                return {"ok": False, "error": "payload missing tool"}
            for attempt in range(max_retries - retry_count + 1):
                out = call_mcp_tool(tool, version, input_data, trace_id=trace_id, timeout_seconds=timeout_seconds)
                if out.get("ok"):
                    self.state_store.set_status(
                        task_id,
                        AgentTask.Status.COMPLETED,
                        result=out.get("output"),
                        finished_at=timezone.now(),
                    )
                    return {"ok": True, "result": out.get("output")}
                if attempt < max_retries - retry_count:
                    self.state_store.increment_retry(task_id)
                    time.sleep(1 * (attempt + 1))
            self.state_store.set_status(
                task_id,
                AgentTask.Status.FAILED,
                error=out.get("error", "mcp_call_failed"),
                finished_at=timezone.now(),
            )
            return {"ok": False, "error": out.get("error")}
