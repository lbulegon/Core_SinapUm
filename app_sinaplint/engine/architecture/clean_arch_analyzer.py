"""
Deteção de dependências entre camadas que violam regras típicas de Clean Architecture.

Regra: dependências devem apontar para dentro (domínio), não o contrário.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from app_sinaplint.engine.architecture.dependency_extractor import DependencyExtractor
from app_sinaplint.engine.architecture.layer_mapper import LayerMapper
from app_sinaplint.engine.graph.django_graph import SKIP_SUBDIR_NAMES, find_django_apps


class CleanArchitectureAnalyzer:
    """
    ``forbidden_targets[source_layer]`` = camadas de destino **proibidas** para essa origem.
    """

    FORBIDDEN_TARGETS: dict[str, list[str]] = {
        "domain": ["application", "presentation", "infrastructure"],
        "application": ["presentation"],
        "presentation": [],
        "infrastructure": [],
        "unknown": [],
    }

    def __init__(self) -> None:
        self._mapper = LayerMapper()
        self._extractor = DependencyExtractor()

    def analyze(self, root: Path) -> list[dict[str, Any]]:
        root = root.resolve()
        violations: list[dict[str, Any]] = []
        seen: set[tuple[str, str, str, str]] = set()
        apps = find_django_apps(root)

        for app in apps:
            app_dir = root / app
            if not app_dir.is_dir():
                continue
            for py in sorted(app_dir.rglob("*.py")):
                if any(part in SKIP_SUBDIR_NAMES for part in py.parts):
                    continue
                try:
                    rel = str(py.relative_to(root))
                except ValueError:
                    rel = str(py)
                source_layer = self._mapper.classify_path(py)
                if source_layer == "unknown":
                    continue
                forbidden = set(self.FORBIDDEN_TARGETS.get(source_layer, []))
                if not forbidden:
                    continue
                for mod in self._extractor.extract(py):
                    target_layer = self._mapper.classify_module(mod)
                    if target_layer == "unknown" or target_layer == source_layer:
                        continue
                    if target_layer not in forbidden:
                        continue
                    key = (rel.replace("\\", "/"), mod, source_layer, target_layer)
                    if key in seen:
                        continue
                    seen.add(key)
                    violations.append(
                        {
                            "type": "clean_arch_violation",
                            "from": key[0],
                            "to_module": mod,
                            "from_layer": source_layer,
                            "to_layer": target_layer,
                        }
                    )
        return violations
