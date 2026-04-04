"""
POST /api/sinaplint/v1/analyze/ — executa SinapLint no código em disco (servidor Django).

Autenticação: header `X-API-KEY` = `SinapLintTenant.api_key`.
Corpo JSON: `{"project_id": <int>}` (projeto deve pertencer ao tenant).
"""

from __future__ import annotations

from pathlib import Path

from django.conf import settings
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.request import Request
from rest_framework.response import Response

from app_sinapcore.models.sinaplint_cloud import SinapLintAnalysis, SinapLintProject, SinapLintTenant
from app_sinaplint.engine import run_analysis


def _tenant_from_request(request: Request) -> SinapLintTenant | None:
    key = request.headers.get("X-API-KEY") or request.META.get("HTTP_X_API_KEY")
    if not key:
        return None
    return SinapLintTenant.objects.filter(api_key=key, is_active=True).first()


@api_view(["POST"])
@permission_classes([AllowAny])
def analyze(request: Request) -> Response:
    tenant = _tenant_from_request(request)
    if not tenant:
        return Response({"error": "Unauthorized"}, status=status.HTTP_403_FORBIDDEN)

    project_id = request.data.get("project_id")
    if project_id is None:
        return Response({"error": "project_id obrigatório"}, status=status.HTTP_400_BAD_REQUEST)

    try:
        project = SinapLintProject.objects.get(id=int(project_id), tenant=tenant)
    except (SinapLintProject.DoesNotExist, ValueError):
        return Response({"error": "Projeto inválido"}, status=status.HTTP_404_NOT_FOUND)

    # BASE_DIR = pasta Core_SinapUm (pai de `setup/`)
    base = Path(getattr(settings, "BASE_DIR", None) or Path(__file__).resolve().parent.parent)
    result = run_analysis(base)

    analysis = SinapLintAnalysis.objects.create(
        project=project,
        score=int(result["score"]),
        result=result,
    )

    return Response(
        {
            "score": result["score"],
            "quality": result["quality"],
            "ok": result["ok"],
            "analysis_id": analysis.id,
            "project_id": project.id,
        },
        status=status.HTTP_200_OK,
    )
