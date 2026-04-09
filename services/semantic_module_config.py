"""Configuração de módulos (merge com Django settings)."""

from __future__ import annotations

from typing import Any

from agent_core.config.settings import MODULE_DEFAULTS


def get_module_config() -> dict[str, dict[str, Any]]:
    try:
        from django.conf import settings as django_settings

        override = getattr(django_settings, "SINAPCORE_MODULES", None)
        if isinstance(override, dict):
            merged = {**MODULE_DEFAULTS}
            for name, cfg in override.items():
                if isinstance(cfg, dict):
                    merged[name] = {**(merged.get(name) or {}), **cfg}
                else:
                    merged[name] = cfg  # type: ignore[assignment]
            return merged
    except Exception:
        pass
    return dict(MODULE_DEFAULTS)
