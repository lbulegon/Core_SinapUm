"""
Motor SinapLint para o produto SinapLint SaaS (orquestração remota).

GET/POST ``/api/sinaplint/internal/engine/`` — retorna o JSON completo (igual ao CLI ``sinaplint check --json``).

- **Sem** ``repo_url`` no corpo (ou GET): analisa a árvore do monólito (``BASE_DIR``).
- **Com** ``repo_url`` (POST JSON): valida HTTPS (GitHub/GitLab/Codeberg), clona com ``git`` para
  diretório temporário e analisa esse clone (produto landing / demo).

Autenticação (recomendado em produção):
  - ``Authorization: Bearer <segredo>`` ou
  - ``X-SinapLint-Engine-Key: <segredo>`` ou
  - ``X-API-KEY: <segredo>``

O segredo é ``settings.SINAPLINT_ENGINE_SHARED_SECRET`` (env ``SINAPLINT_ENGINE_SHARED_SECRET``).
Se não estiver definido: com ``DEBUG`` permite (dev); em produção responde 503.
"""

from __future__ import annotations

from pathlib import Path

from django.conf import settings
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.request import Request
from rest_framework.response import Response

from app_sinapcore.services.sinaplint_service import SinapLintService
from app_sinaplint.services.public_repo_clone import (
    SinapLintRepoError,
    temporary_clone,
    validate_public_repo_url,
)


def _auth_error_or_none(request: Request) -> Response | None:
    secret = (getattr(settings, "SINAPLINT_ENGINE_SHARED_SECRET", None) or "").strip()
    if not secret:
        if settings.DEBUG:
            return None
        return Response(
            {
                "error": "SINAPLINT_ENGINE_SHARED_SECRET não configurado",
                "hint": "Configure a variável de ambiente no Core (e o mesmo valor no SinapLint como SINAPLINT_ENGINE_API_KEY).",
            },
            status=status.HTTP_503_SERVICE_UNAVAILABLE,
        )

    token = (
        request.headers.get("X-SinapLint-Engine-Key")
        or request.META.get("HTTP_X_SINAPLINT_ENGINE_KEY")
        or request.headers.get("X-API-KEY")
        or request.META.get("HTTP_X_API_KEY")
        or ""
    ).strip()
    auth = request.headers.get("Authorization") or ""
    if auth.startswith("Bearer "):
        token = auth[7:].strip() or token

    if token != secret:
        return Response({"error": "Unauthorized"}, status=status.HTTP_403_FORBIDDEN)
    return None


def _resolve_repo_url(request: Request) -> tuple[str | None, Response | None]:
    """
    Se POST JSON incluir ``repo_url`` não vazio, valida o URL HTTPS.
    Devolve (url_normalizado, None) ou (None, Response 400).
    """
    if request.method != "POST":
        return None, None
    data = request.data if isinstance(getattr(request, "data", None), dict) else {}
    raw = data.get("repo_url")
    if not isinstance(raw, str) or not raw.strip():
        return None, None
    norm, verr = validate_public_repo_url(raw.strip())
    if verr or not norm:
        return None, Response(
            {"error": "invalid_repo_url", "detail": verr or "URL inválida."},
            status=status.HTTP_400_BAD_REQUEST,
        )
    return norm, None


@api_view(["GET", "POST"])
@permission_classes([AllowAny])
def engine_run(request: Request) -> Response:
    err = _auth_error_or_none(request)
    if err is not None:
        return err

    repo_url, bad = _resolve_repo_url(request)
    if bad is not None:
        return bad

    if repo_url:
        try:
            with temporary_clone(repo_url) as cloned:
                result = SinapLintService().analyze(cloned)
        except SinapLintRepoError as exc:
            return Response(
                {"error": "clone_failed", "detail": str(exc)},
                status=getattr(exc, "status_code", 502),
            )
        except Exception as exc:
            return Response(
                {"error": "sinaplint_failed", "detail": str(exc)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
        return Response(result, status=status.HTTP_200_OK)

    # BASE_DIR = raiz do monólito Core_SinapUm (pai de setup/)
    base = Path(getattr(settings, "BASE_DIR", Path(__file__).resolve().parent.parent))
    try:
        result = SinapLintService().analyze(base)
    except Exception as exc:
        return Response(
            {"error": "sinaplint_failed", "detail": str(exc)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )
    return Response(result, status=status.HTTP_200_OK)
