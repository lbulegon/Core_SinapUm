"""
Classificação heurística de camadas (Clean Architecture / DDD em projetos Django).

``presentation`` · ``application`` · ``domain`` · ``infrastructure`` · ``unknown``
"""

from __future__ import annotations

from pathlib import Path


class LayerMapper:
    """Mapeia caminhos de ficheiro e nomes de módulo para camadas lógicas."""

    def classify_path(self, file_path: Path | str) -> str:
        """Classifica um ficheiro ``.py`` pela sua localização na árvore."""
        s = str(file_path).lower().replace("\\", "/")
        if "migrations" in s:
            return "infrastructure"
        if "/views/" in s or s.endswith("/views.py") or "/views.py" in s:
            return "presentation"
        if "serializers" in s or "/forms/" in s or "/forms.py" in s:
            return "presentation"
        if "/services/" in s or "/use_cases/" in s or "services.py" in s:
            return "application"
        if "/models/" in s or s.endswith("/models.py") or "/models.py" in s:
            return "domain"
        if "repositories" in s or "adapters" in s or "/infra/" in s:
            return "infrastructure"
        if "/api/" in s and ("view" in s or "views" in s):
            return "presentation"
        return "unknown"

    def classify_module(self, module: str) -> str:
        """Classifica um módulo importado (ex.: ``app_orders.views``)."""
        m = module.lower().strip()
        if not m:
            return "unknown"
        parts = m.split(".")
        if "migrations" in parts:
            return "infrastructure"
        if "views" in parts or "viewsets" in parts or "serializers" in parts:
            return "presentation"
        if "forms" in parts:
            return "presentation"
        if "services" in parts or "use_cases" in parts:
            return "application"
        if "models" in parts:
            return "domain"
        if "repositories" in parts or "adapters" in parts:
            return "infrastructure"
        if "admin" in parts:
            return "presentation"
        return "unknown"
