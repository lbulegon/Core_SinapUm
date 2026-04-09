"""
Testes unitários do ExecutorAgent (sync path com mock de requests).
PR5 — Hardening + testes.
"""
import sys
from pathlib import Path
from unittest.mock import patch, MagicMock

_root = Path(__file__).resolve().parents[2]
if str(_root) not in sys.path:
    sys.path.insert(0, str(_root))

from a2a.executor_agent import ExecutorAgent
from a2a.schemas import A2APlan, PlanStep


def _noop_plan():
    return A2APlan(
        intent="fallback_safe",
        steps=[PlanStep(id="step_1", tool_name="noop", tool_version="1.0", args={"reason": "test"})],
    )


class TestExecutorAgentSync:
    """ExecutorAgent com use_acp=False (sync via /mcp/call)."""

    @patch("requests.post")
    def test_execute_sync_returns_completed_on_ok(self, mock_post):
        mock_post.return_value = MagicMock(
            content=b'{"ok": true, "output": {"message": "No operation - tool not implemented"}}',
            status_code=200,
        )
        mock_post.return_value.json.return_value = {
            "ok": True,
            "output": {"message": "No operation - tool not implemented"},
        }
        executor = ExecutorAgent(use_acp=False)
        plan = _noop_plan()
        result = executor.execute(plan=plan, trace_id="test-trace")
        assert result["status"] == "COMPLETED"
        assert result["trace_id"] == "test-trace"
        assert result["task_id"] is None
        assert result.get("result") is not None

    @patch("requests.post")
    def test_execute_sync_returns_failed_on_not_ok(self, mock_post):
        mock_post.return_value = MagicMock(
            content=b'{"ok": false, "error": "Tool error"}',
            status_code=500,
        )
        mock_post.return_value.json.return_value = {"ok": False, "error": "Tool error"}
        executor = ExecutorAgent(use_acp=False)
        plan = _noop_plan()
        result = executor.execute(plan=plan, trace_id="test-trace-2")
        assert result["status"] == "FAILED"
        assert "error" in result
