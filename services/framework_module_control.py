"""Snapshot de módulos registados / BD (debug, health)."""

from __future__ import annotations

from typing import Any


def describe_registered_modules() -> list[dict[str, Any]]:
    try:
        from django.apps import apps

        if apps.ready:
            from app_sinapcore.models.sinapcore_module import SinapCoreModule

            return [
                {
                    "name": m.name,
                    "priority": m.priority,
                    "enabled": m.enabled,
                    "source": "database",
                }
                for m in SinapCoreModule.objects.order_by("priority", "name")
            ]
    except Exception:
        pass

    from agent_core.registry.module_registry import ModuleRegistry

    return [
        {
            "name": m.name,
            "priority": m.priority,
            "enabled": m.enabled,
            "source": "static_registry",
        }
        for m in ModuleRegistry.all_modules()
    ]
