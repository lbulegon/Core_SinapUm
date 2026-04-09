"""
Painel humano do Agent Core — observabilidade do ciclo PAOR e governança.
"""

from __future__ import annotations

import logging

from django.contrib import messages
from django.shortcuts import redirect, render
from django.views.decorators.http import require_http_methods

from agent_core.models.agent_run import AgentRun

logger = logging.getLogger(__name__)

# Bundle padrão no container (volume /app); se não existir, a avaliação usa mock.
DEFAULT_BUNDLE = "/app/docs/architecture_bundle/mrfoo_architecture_bundle"


def dashboard(request):
    runs = AgentRun.objects.order_by("-created_at")[:25]
    context = {
        "runs": runs,
        "total_runs": AgentRun.objects.count(),
    }
    return render(request, "agent_core/dashboard.html", context)


@require_http_methods(["POST"])
def run_demo_cycle(request):
    """
    Dispara um ciclo cognitivo de demonstração (Grand Jury local, rápido) e persiste AgentRun.
    Exige CSRF (formulário no dashboard).
    """
    from agent_core.policies.chef_agno import ChefAgnoPolicy
    from agent_core.services.cognitive_cycle_service import CognitiveCycleService

    bundle_path = (request.POST.get("bundle_path") or DEFAULT_BUNDLE).strip()
    policy = ChefAgnoPolicy(
        name="chef_agno_demo",
        max_iterations=3,
        priorities=("demonstracao",),
        success_criteria={"require_all_steps_ok": True},
    )
    semantic_context = {
        "allowed_operations": ["noop", "dispatch"],
        "required_result_keys": ["ok"],
    }

    try:
        service = CognitiveCycleService.with_simulated_orbital()
        run = service.run_with_architecture_governance(
            objective="Demonstração — ciclo PAOR com parecer institucional (Grand Jury)",
            policy=policy,
            semantic_context=semantic_context,
            bundle_path=bundle_path,
            evaluation_mode="grand_jury",
        )
        messages.success(
            request,
            f"Ciclo concluído — run {run.id} · status {run.status}",
        )
    except Exception as exc:  # noqa: BLE001
        logger.exception("run_demo_cycle falhou")
        messages.error(request, f"Falha ao executar demonstração: {exc}")

    return redirect("/agent-core/dashboard/")
