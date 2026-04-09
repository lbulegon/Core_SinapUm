"""
Endpoints HTTP do Agent Core — integração com Architecture Intelligence (opcional).

Não substitui chamadas internas Python; use `CognitiveCycleService` direto no Core quando possível.
"""

from __future__ import annotations

import json
import logging

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

from agent_core.adapters.architecture_intelligence_adapter import ArchitectureIntelligenceAdapter
from agent_core.policies.chef_agno import ChefAgnoPolicy
from agent_core.services.cognitive_cycle_service import CognitiveCycleService

logger = logging.getLogger(__name__)


@require_http_methods(["GET"])
def health(request):
    return JsonResponse({"app": "agent_core", "status": "ok"})


@csrf_exempt
@require_http_methods(["POST"])
def run_with_governance(request):
    """
    POST /agent-core/run-with-governance/

    Corpo JSON (mínimo):
      - bundle_path: str
      - objective: str (opcional)

    Opcional:
      - evaluation_mode, system_name, system_type
      - semantic_context: dict (restrições / operações do Core)
      - use_http_ai: bool — se true, chama Architecture Intelligence via HTTP
      - ai_base_url: str — ex.: https://host:5000 (sem barra final)
      - max_iterations, priorities (lista)
    """
    try:
        body = json.loads(request.body.decode() or "{}")
    except json.JSONDecodeError:
        return JsonResponse({"error": "JSON inválido"}, status=400)

    bundle_path = (body.get("bundle_path") or "").strip()
    if not bundle_path:
        return JsonResponse({"error": "bundle_path é obrigatório"}, status=400)

    objective = (body.get("objective") or "execução cognitiva com governança").strip()
    evaluation_mode = (body.get("evaluation_mode") or "full_cycle").strip()
    system_name = (body.get("system_name") or "MrFoo").strip()
    system_type = (body.get("system_type") or "Orbital").strip()
    use_http = bool(body.get("use_http_ai"))
    base_url = (body.get("ai_base_url") or "").strip() or None
    trace_id = body.get("trace_id")

    priorities = body.get("priorities")
    if isinstance(priorities, list) and priorities:
        prios: tuple[str, ...] = tuple(str(p) for p in priorities)
    else:
        prios = ("default",)

    policy = ChefAgnoPolicy(
        max_iterations=int(body.get("max_iterations", 5)),
        priorities=prios,
    )

    semantic_context = body.get("semantic_context")
    if not isinstance(semantic_context, dict):
        semantic_context = {}
    semantic_context = dict(semantic_context)
    if "required_result_keys" not in semantic_context:
        semantic_context["required_result_keys"] = ["ok"]

    adapter = ArchitectureIntelligenceAdapter(use_http=use_http, base_url=base_url)
    service = CognitiveCycleService.with_simulated_orbital()

    try:
        run = service.run_with_architecture_governance(
            objective=objective,
            policy=policy,
            semantic_context=semantic_context,
            bundle_path=bundle_path,
            evaluation_mode=evaluation_mode,
            system_name=system_name,
            system_type=system_type,
            architecture_adapter=adapter,
            trace_id=trace_id,
        )
    except Exception as exc:  # noqa: BLE001
        logger.exception("run_with_governance falhou")
        return JsonResponse({"error": str(exc)}, status=500)

    return JsonResponse(
        {
            "id": str(run.id),
            "status": run.status,
            "iteracao": run.iteracao,
            "plano": run.plano,
            "estado_atual": run.estado_atual,
            "historico_fases": [h.get("phase") for h in (run.historico or [])],
        }
    )
