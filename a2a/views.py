"""
Views A2A — POST /a2a/run e GET /a2a/tasks/<task_id> (proxy para ACP).
PR3: Feature flags A2A_ENABLED, ACP_ENABLED, DUAL_RUN_ENABLED; fallback e dual-run.
"""
import json
import logging
import uuid
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

logger = logging.getLogger(__name__)


def _a2a_enabled() -> bool:
    """A2A_ENABLED: default True (ON)."""
    try:
        from core.services.feature_flags import is_enabled
        return is_enabled("A2A_ENABLED", default=True)
    except Exception:
        return True


def _acp_enabled() -> bool:
    """ACP_ENABLED: default True (ON). Se false, /a2a/run executa síncrono via MCP."""
    try:
        from core.services.feature_flags import is_enabled
        return is_enabled("ACP_ENABLED", default=True)
    except Exception:
        return True


def _dual_run_enabled() -> bool:
    """DUAL_RUN_ENABLED: default False. Executa legado/sync + ACP e loga divergência."""
    try:
        from core.services.feature_flags import is_enabled
        return is_enabled("DUAL_RUN_ENABLED", default=False)
    except Exception:
        return False


@csrf_exempt
@require_http_methods(["POST"])
def run(request):
    """
    POST /a2a/run
    Body: { "input": "...", "context": {}, "idempotency_key": "opcional" }
    Response: { "trace_id", "task_id", "status", "result" }
    Se ACP_ENABLED=false: execução síncrona via MCP (retorna result no response).
    Se DUAL_RUN_ENABLED=true: executa também caminho alternativo e loga divergência (best effort).
    """
    if not _a2a_enabled():
        return JsonResponse({"error": "A2A is disabled", "code": "A2A_DISABLED"}, status=503)
    try:
        body = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({"error": "JSON inválido"}, status=400)
    user_input = body.get("input", "").strip()
    context = body.get("context") or {}
    idempotency_key = body.get("idempotency_key")
    cognitive_context = body.get("cognitive_context")
    reality_state = body.get("reality_state")
    decision_hints = body.get("decision_hints")
    if not user_input:
        return JsonResponse({"error": "Campo 'input' é obrigatório"}, status=400)

    from .planner_agent import PlannerAgent
    from .executor_agent import ExecutorAgent

    planner = PlannerAgent()
    plan = planner.plan(
        user_input=user_input,
        context=context,
        cognitive_context=cognitive_context,
        reality_state=reality_state,
        decision_hints=decision_hints,
    )
    trace_id = str(uuid.uuid4())
    use_acp = _acp_enabled()

    # Dual-run: executar caminho alternativo (sync) e logar para comparação
    if _dual_run_enabled():
        try:
            executor_sync = ExecutorAgent(use_acp=False)
            sync_result = executor_sync.execute(
                plan=plan,
                context=context,
                trace_id=trace_id,
                idempotency_key=None,
            )
            logger.info(
                "dual_run sync path trace_id=%s status=%s result_keys=%s",
                trace_id,
                sync_result.get("status"),
                list((sync_result.get("result") or {}).keys()) if isinstance(sync_result.get("result"), dict) else None,
            )
        except Exception as e:
            logger.warning("dual_run sync path failed trace_id=%s error=%s", trace_id, e)

    # Caminho principal: ACP ou sync conforme flag
    executor = ExecutorAgent(use_acp=use_acp)
    result = executor.execute(
        plan=plan,
        context=context,
        trace_id=trace_id,
        idempotency_key=idempotency_key,
    )
    return JsonResponse(result, status=200)


@require_http_methods(["GET"])
def get_task(request, task_id):
    """
    GET /a2a/tasks/<task_id>/
    Proxy para GET /acp/tasks/<task_id>/
    """
    from app_acp.task_manager import TaskManager
    manager = TaskManager()
    state = manager.get_task(str(task_id))
    if not state:
        return JsonResponse({"error": "Tarefa não encontrada", "task_id": str(task_id)}, status=404)
    return JsonResponse(state)
