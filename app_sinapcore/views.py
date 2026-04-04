"""
Dashboard SinapCore + logs de auditoria (fora do Admin).
"""

from __future__ import annotations

from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from app_sinapcore.models.sinapcore_log import SinapCoreLog
from app_sinapcore.models.sinapcore_module import SinapCoreModule


@staff_member_required
def sinapcore_dashboard(request):
    modules = SinapCoreModule.objects.all().order_by("priority", "name")
    return render(
        request,
        "sinapcore/dashboard.html",
        {"modules": modules},
    )


@staff_member_required
@require_POST
def toggle_module(request, module_id: int):
    module = get_object_or_404(SinapCoreModule, id=module_id)
    module.enabled = not module.enabled
    module.save(update_fields=["enabled", "updated_at"])
    return redirect("sinapcore_dashboard")


@staff_member_required
def module_logs(request, module_name: str):
    logs = SinapCoreLog.objects.filter(module=module_name).order_by("-timestamp")[:100]
    return render(
        request,
        "sinapcore/logs.html",
        {"logs": logs, "module": module_name},
    )
