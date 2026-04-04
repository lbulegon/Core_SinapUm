"""
EOC — Centro de Operações Cognitivo (torre SinapCore + ambiente + decisões + comando).
"""

from __future__ import annotations

from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import redirect, render
from django.views.decorators.http import require_POST

from app_sinapcore.models.architecture_score import ArchitectureScore
from app_sinapcore.models.sinapcore_command import SinapCoreCommand
from app_sinapcore.models.sinapcore_log import SinapCoreLog
from app_sinapcore.models.sinapcore_module import SinapCoreModule
from services.alert_service import AlertService
from services.command_executor import CommandExecutor
from services.environmental_state_service import EnvironmentalStateService
from services.system_mode_service import compute_mode_from_env_dict

_DEFAULT_ENV = {
    "score": 0.0,
    "state": "estavel",
    "confidence": 0.0,
    "indicios": {},
}


@staff_member_required
def eoc_dashboard(request, estabelecimento_id: int = 1):
    modules = SinapCoreModule.objects.filter(enabled=True).order_by("priority", "name")
    logs = SinapCoreLog.objects.all().order_by("-timestamp")[:20]
    raw = EnvironmentalStateService.get_state(estabelecimento_id)
    env = raw if raw is not None else dict(_DEFAULT_ENV)
    no_env_data = raw is None
    system_mode = compute_mode_from_env_dict(raw)

    pattern_alert = AlertService.check_environmental_alerts()
    recent_commands = SinapCoreCommand.objects.all()[:15]

    lint_last = ArchitectureScore.objects.order_by("-created_at").first()
    sinaplint_ctx = {
        "score": lint_last.score if lint_last else None,
        "quality": lint_last.quality if lint_last else None,
        "passed": lint_last.passed if lint_last else None,
        "created_at": lint_last.created_at if lint_last else None,
        "has_data": lint_last is not None,
    }

    return render(
        request,
        "eoc/dashboard.html",
        {
            "modules": modules,
            "logs": logs,
            "env": env,
            "estabelecimento_id": estabelecimento_id,
            "no_env_data": no_env_data,
            "pattern_alert": pattern_alert,
            "system_mode": system_mode,
            "recent_commands": recent_commands,
            "sinaplint": sinaplint_ctx,
        },
    )


@staff_member_required
@require_POST
def eoc_send_command(request):
    cmd = request.POST.get("command")
    eid_raw = request.POST.get("estabelecimento_id", "1")
    try:
        eid = int(eid_raw)
    except (TypeError, ValueError):
        eid = 1

    valid = {c[0] for c in SinapCoreCommand.COMMAND_TYPES}
    if cmd not in valid:
        return redirect("eoc_dashboard_establishment", estabelecimento_id=eid)

    SinapCoreCommand.objects.create(command=cmd, status="pending", source="manual")
    SinapCoreLog.objects.create(
        module="EOC",
        decision="manual_command",
        action=cmd,
        context={"estabelecimento_id": eid},
    )
    try:
        CommandExecutor.execute_pending({"estabelecimento_id": eid})
    except Exception:
        pass

    return redirect("eoc_dashboard_establishment", estabelecimento_id=eid)
