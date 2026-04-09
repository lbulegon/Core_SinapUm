"""
Resolução de módulos ativos (BD + fallback estático).
"""

from __future__ import annotations

import logging
from typing import Any

from services.semantic_module_config import get_module_config

logger = logging.getLogger(__name__)


def resolve_active_modules() -> list[Any]:
    from agent_core.registry.module_registry import ModuleDescriptor, ModuleRegistry

    ModuleRegistry._ensure_module_map()  # noqa: SLF001
    try:
        from django.apps import apps

        if not apps.ready:
            return ModuleRegistry._get_static_active_modules()  # noqa: SLF001

        from app_sinapcore.models.sinapcore_module import SinapCoreModule

        qs = SinapCoreModule.objects.filter(enabled=True).order_by("priority", "name")
        if qs.exists():
            out: list[ModuleDescriptor] = []
            for row in qs:
                mod_cls = ModuleRegistry.MODULE_MAP.get(row.name)
                if mod_cls is None:
                    logger.warning("Módulo desconhecido na BD (ignorado): %s", row.name)
                    continue
                try:
                    instance = mod_cls(config=row)
                    out.append(instance.to_descriptor())
                except Exception:
                    logger.exception("Falha ao instanciar módulo %s", row.name)
            if out:
                return out
    except Exception:
        logger.exception("Leitura BD módulos falhou; fallback estático")

    return ModuleRegistry._get_static_active_modules()  # noqa: SLF001
