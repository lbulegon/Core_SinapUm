"""
API interna MarketFish ↔ Core_SinapUm.

POST /sinapum/tasks/create/ — regista tarefa orquestrada; devolve orchestration_id.
POST /sinapum/tasks/result/ — consolida resultado vindo do MarketFish.

Autenticação: Authorization: Bearer <INTERNAL_API_TOKEN>
"""

from __future__ import annotations

import json
import logging
import uuid

from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from app_sinapum.models import OrchestratedHumanTask

logger = logging.getLogger(__name__)


def _unauthorized():
    return JsonResponse({"detail": "Token inválido ou em falta."}, status=401)


def _require_internal_token(request):
    expected = (getattr(settings, "INTERNAL_API_TOKEN", None) or "").strip()
    if not expected:
        logger.warning("INTERNAL_API_TOKEN não configurado — rotas MarketFish bloqueadas.")
        return False
    auth = (request.headers.get("Authorization") or "").strip()
    if not auth.startswith("Bearer "):
        return False
    token = auth[7:].strip()
    return token == expected


@csrf_exempt
@require_POST
def create_task(request):
    if not _require_internal_token(request):
        return _unauthorized()
    try:
        body = json.loads(request.body.decode("utf-8") or "{}")
    except json.JSONDecodeError:
        return JsonResponse({"detail": "JSON inválido."}, status=400)

    title = (body.get("title") or "Tarefa humana").strip()[:255]
    text_body = (body.get("body") or "").strip()
    if not text_body:
        text_body = (
            "Classifique o seguinte texto como positivo, neutro ou negativo: "
            "'O serviço foi rápido e cordial.'"
        )
    min_r = int(body.get("min_responses") or 3)
    if min_r < 1:
        min_r = 1
    if min_r > 50:
        min_r = 50

    row = OrchestratedHumanTask.objects.create(
        title=title,
        body=text_body,
        min_responses=min_r,
        status=OrchestratedHumanTask.Status.OPEN,
    )
    interaction_type = (body.get("interaction_type") or "freeform").strip()
    task_kind = (body.get("task_kind") or "validation").strip()
    ai_payload = body.get("ai_payload")
    input_data = body.get("input_data")
    if not isinstance(ai_payload, dict):
        ai_payload = {}
    if not isinstance(input_data, dict):
        input_data = {}
    valor_raw = body.get("valor_total") or body.get("valor") or "0"
    return JsonResponse(
        {
            "orchestration_id": str(row.orchestration_id),
            "title": row.title,
            "body": row.body,
            "min_responses": row.min_responses,
            "interaction_type": interaction_type,
            "task_kind": task_kind,
            "ai_payload": ai_payload,
            "input_data": input_data or ai_payload,
            "valor_total": str(valor_raw).strip(),
        }
    )


@csrf_exempt
@require_POST
def receive_result(request):
    if not _require_internal_token(request):
        return _unauthorized()
    try:
        body = json.loads(request.body.decode("utf-8") or "{}")
    except json.JSONDecodeError:
        return JsonResponse({"detail": "JSON inválido."}, status=400)

    oid_raw = body.get("orchestration_id")
    try:
        oid = uuid.UUID(str(oid_raw))
    except (ValueError, TypeError):
        return JsonResponse({"detail": "orchestration_id inválido."}, status=400)

    try:
        row = OrchestratedHumanTask.objects.get(orchestration_id=oid)
    except OrchestratedHumanTask.DoesNotExist:
        return JsonResponse({"detail": "Tarefa não encontrada."}, status=404)

    row.status = OrchestratedHumanTask.Status.RESULT_RECEIVED
    row.result_payload = {
        "final_result": body.get("final_result"),
        "consensus_meta": body.get("consensus_meta") or {},
        "task_public_id": body.get("task_public_id"),
    }
    row.save(update_fields=["status", "result_payload", "updated_at"])

    # Ponto de extensão: alimentar pipelines cognitivos / IA com row.result_payload
    logger.info(
        "MarketFish consolidou task orchestration_id=%s public_id=%s",
        oid,
        body.get("task_public_id"),
    )

    return JsonResponse({"detail": "ok", "orchestration_id": str(oid)})
