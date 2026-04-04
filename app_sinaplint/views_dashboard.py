"""
Dashboard SaaS: resumo, histórico de análises, billing.
"""

from __future__ import annotations

from datetime import date

from django.contrib.auth.models import AbstractUser
from django.utils import timezone
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from app_sinaplint.models_billing import Subscription
from app_sinaplint.models_repository import Analysis, AnalysisDelta
from app_sinaplint.models_usage import Usage
from app_sinaplint.services.usage_limits import get_effective_plan


def _month_start(d: date | None = None) -> date:
    if d is None:
        d = timezone.now().date()
    return date(d.year, d.month, 1)


def build_summary_payload(user: AbstractUser) -> dict:
    plan = get_effective_plan(user)
    m = _month_start()
    usage = Usage.objects.filter(user=user, month=m).first()
    used = int(usage.analyses_count) if usage else 0
    limit = int(plan.max_analyses_per_month) if plan else 0
    repo_count = user.sinaplint_repositories.count()
    max_repos = int(plan.max_repos) if plan else 0

    return {
        "plan": {
            "name": plan.name if plan else "—",
            "slug": plan.slug if plan else None,
            "max_analyses_per_month": limit,
            "max_repos": max_repos,
        },
        "usage": {
            "used": used,
            "limit": limit,
            "unlimited": limit < 0,
            "repos_used": repo_count,
            "repos_limit": max_repos,
        },
    }


def build_history_payload(user: AbstractUser, limit: int = 50) -> list[dict]:
    limit = min(max(limit, 1), 200)
    qs = (
        Analysis.objects.filter(repository__user=user)
        .select_related("repository")
        .order_by("-created_at")[:limit]
    )
    analysis_ids = [a.id for a in qs]
    deltas = {
        d.analysis_id: d
        for d in AnalysisDelta.objects.filter(analysis_id__in=analysis_ids)
    }
    data: list[dict] = []
    for a in qs:
        row = {
            "id": a.id,
            "repo": a.repository.name,
            "repo_url": a.repository.url,
            "score": a.score,
            "architecture_score": a.architecture_score,
            "branch": a.branch,
            "commit_hash": a.commit_hash,
            "created_at": a.created_at.isoformat(),
        }
        d = deltas.get(a.id)
        if d:
            row["delta"] = {
                "score_change": d.score_change,
                "new_cycles": d.new_cycles,
                "coupling_increased": d.coupling_increased,
            }
        data.append(row)
    return data


def build_billing_payload(user: AbstractUser) -> dict:
    plan = get_effective_plan(user)
    sub = Subscription.objects.filter(user=user).first()
    return {
        "plan": {
            "name": plan.name if plan else "—",
            "slug": plan.slug if plan else None,
        },
        "subscription": (
            {
                "status": sub.status,
                "stripe_customer_id": sub.stripe_customer_id or None,
                "current_period_end": sub.current_period_end.isoformat()
                if sub.current_period_end
                else None,
            }
            if sub
            else None
        ),
    }


class DashboardSummaryView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request: Request) -> Response:
        return Response(build_summary_payload(request.user))


class DashboardHistoryView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request: Request) -> Response:
        lim = int(request.query_params.get("limit", "50"))
        return Response(build_history_payload(request.user, lim))


class DashboardBillingView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request: Request) -> Response:
        return Response(build_billing_payload(request.user))


class DashboardOverviewView(APIView):
    """Resposta agregada para a SPA (um único GET)."""

    permission_classes = [IsAuthenticated]

    def get(self, request: Request) -> Response:
        lim = int(request.query_params.get("limit", "50"))
        return Response(
            {
                "summary": build_summary_payload(request.user),
                "history": build_history_payload(request.user, lim),
                "billing": build_billing_payload(request.user),
            }
        )
