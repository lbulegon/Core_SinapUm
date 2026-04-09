"""
Views ACP — API para criar, consultar e cancelar tarefas de agente.

Rotas: POST /acp/tasks/, GET /acp/tasks/<task_id>/, POST /acp/tasks/<task_id>/cancel/
"""
import json
import logging
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

from .task_manager import TaskManager

logger = logging.getLogger(__name__)
task_manager = TaskManager()


@csrf_exempt
@require_http_methods(["POST"])
def create_task(request):
    """
    POST /acp/tasks/
    Body: { "agent_name": "...", "payload": {...}, "trace_id?", "max_retries?", "timeout_seconds?", "idempotency_key?" }
    """
    try:
        body = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({"error": "JSON inválido"}, status=400)
    agent_name = body.get("agent_name")
    payload = body.get("payload", body)
    if not agent_name:
        return JsonResponse({"error": "agent_name é obrigatório"}, status=400)
    trace_id = body.get("trace_id")
    max_retries = body.get("max_retries", 3)
    timeout_seconds = body.get("timeout_seconds")
    idempotency_key = body.get("idempotency_key")
    result = task_manager.create_task(
        agent_name=agent_name,
        payload=payload,
        trace_id=trace_id,
        max_retries=max_retries,
        timeout_seconds=timeout_seconds,
        idempotency_key=idempotency_key,
    )
    return JsonResponse(result, status=201)


@require_http_methods(["GET"])
def get_task(request, task_id):
    """
    GET /acp/tasks/<task_id>/
    Retorna estado da tarefa.
    """
    state = task_manager.get_task(str(task_id))
    if not state:
        return JsonResponse({"error": "Tarefa não encontrada", "task_id": str(task_id)}, status=404)
    return JsonResponse(state)


@csrf_exempt
@require_http_methods(["POST"])
def cancel_task(request, task_id):
    """
    POST /acp/tasks/<task_id>/cancel/
    Cancela tarefa se ainda PENDING ou WAITING.
    """
    task_id_str = str(task_id)
    ok = task_manager.cancel_task(task_id_str)
    if not ok:
        state = task_manager.get_task(task_id_str)
        return JsonResponse({
            "cancelled": False,
            "message": "Tarefa não encontrada ou já em execução/concluída",
            "task_id": task_id_str,
            "status": state.get("status") if state else None,
        }, status=400)
    return JsonResponse({"cancelled": True, "task_id": task_id_str})
