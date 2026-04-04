"""
Análise com controlo de uso (plano + contagem mensal).

Requer utilizador autenticado (sessão ou ``X-API-Key`` via middleware).

Corpo JSON opcional para histórico:

- ``repository_id`` — analisa e grava em :class:`~app_sinaplint.models_repository.Repository` existente.
- ``repo_url`` (+ ``repo_name``, ``provider``) — obtém ou cria repositório (limite ``max_repos``).
- ``commit_hash``, ``branch`` — metadados da análise.
"""

from __future__ import annotations

from pathlib import Path

from django.conf import settings
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response

from app_sinaplint.engine import run_analysis
from app_sinaplint.models_repository import Analysis, AnalysisDelta, Repository
from app_sinaplint.services.repo_limits import RepoLimitExceeded, ensure_repository_for_user
from app_sinaplint.services.usage_limits import UsageLimitExceeded, check_and_increment_usage


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def analyze_with_usage(request: Request) -> Response:
    """
    Executa ``run_analysis`` na raiz do projeto (ou ``path`` em JSON, relativo e validado).

    Incrementa o contador de uso **após** verificação de limite.
    """
    user = request.user
    repo: Repository | None = None

    rid = request.data.get("repository_id")
    repo_url = request.data.get("repo_url")

    if rid is not None:
        try:
            repo = Repository.objects.filter(pk=int(rid), user=user).first()
        except (TypeError, ValueError):
            repo = None
        if not repo:
            return Response(
                {"error": "repository_id inválido"},
                status=status.HTTP_400_BAD_REQUEST,
            )
    elif repo_url:
        try:
            repo = ensure_repository_for_user(
                user,
                str(repo_url).strip(),
                name=request.data.get("repo_name"),
                provider=str(request.data.get("provider") or "github"),
            )
        except RepoLimitExceeded as e:
            return Response(
                {
                    "error": str(e),
                    "limit": e.limit,
                    "used": e.used,
                    "code": "repo_limit_exceeded",
                },
                status=status.HTTP_402_PAYMENT_REQUIRED,
            )

    try:
        check_and_increment_usage(user)
    except UsageLimitExceeded as e:
        return Response(
            {
                "error": str(e),
                "limit": e.limit,
                "used": e.used,
                "code": "usage_limit_exceeded",
            },
            status=status.HTTP_402_PAYMENT_REQUIRED,
        )

    base = Path(getattr(settings, "BASE_DIR", Path(__file__).resolve().parent.parent))
    raw_path = request.data.get("path")
    if raw_path:
        candidate = (base / str(raw_path)).resolve()
        try:
            candidate.relative_to(base.resolve())
        except ValueError:
            return Response(
                {"error": "path inválido (fora da raiz do projeto)"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if not candidate.is_dir():
            return Response({"error": "path não é diretório"}, status=status.HTTP_400_BAD_REQUEST)
        base = candidate

    result = run_analysis(base)

    if repo:
        scores = result.get("scores") or {}
        arch_raw = scores.get("architecture")
        arch_s = int(arch_raw) if arch_raw is not None else None
        analysis = Analysis.objects.create(
            repository=repo,
            commit_hash=(request.data.get("commit_hash") or None),
            branch=(request.data.get("branch") or None),
            score=int(result.get("score") or 0),
            architecture_score=arch_s,
            result=result,
        )
        delta = result.get("delta") or {}
        if delta.get("base_available"):
            AnalysisDelta.objects.create(
                analysis=analysis,
                score_change=int(delta.get("score_change") or 0),
                new_cycles=int(
                    delta.get("new_cycles_count") or delta.get("new_cycles") or 0
                ),
                coupling_increased=bool(delta.get("coupling_increased")),
            )

    return Response(result, status=status.HTTP_200_OK)
