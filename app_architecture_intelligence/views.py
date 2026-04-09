"""
Views do Architecture Intelligence - Interface de avaliação arquitetural.
"""
import json
import logging
from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt

from . import services

logger = logging.getLogger(__name__)


@require_http_methods(["GET"])
def dashboard(request):
    """
    Página principal do módulo Architecture Intelligence.
    GET /architecture/
    """
    return render(request, "app_architecture_intelligence/dashboard.html")


@csrf_exempt
@require_http_methods(["POST"])
def evaluate(request):
    """
    Endpoint de avaliação arquitetural.
    POST /architecture/evaluate
    Payload: { system_name, system_type, bundle_path, evaluation_mode }
    """
    try:
        body = json.loads(request.body) if request.body else {}
    except json.JSONDecodeError:
        return JsonResponse({"error": "JSON inválido"}, status=400)

    system_name = body.get("system_name", "MrFoo").strip() or "MrFoo"
    system_type = body.get("system_type", "Orbital").strip() or "Orbital"
    bundle_path = body.get("bundle_path", "/app/docs/architecture_bundle/mrfoo_architecture_bundle").strip()
    evaluation_mode = body.get("evaluation_mode", "full_cycle").strip() or "full_cycle"

    if not bundle_path:
        return JsonResponse({"error": "bundle_path é obrigatório"}, status=400)

    try:
        result = services.start_architecture_evaluation(
            system_name=system_name,
            system_type=system_type,
            bundle_path=bundle_path,
            evaluation_mode=evaluation_mode,
        )
        return JsonResponse(result)
    except FileNotFoundError as e:
        return JsonResponse({"error": str(e)}, status=404)
    except Exception as e:
        logger.exception("Erro na avaliação arquitetural")
        return JsonResponse({"error": str(e)}, status=500)
