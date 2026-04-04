"""Caminhos e exclusões partilhadas pelas regras SinapLint."""

from __future__ import annotations

from pathlib import Path

SKIP_DIR_NAMES = frozenset(
    {
        ".git",
        "__pycache__",
        ".venv",
        "venv",
        "node_modules",
        ".mypy_cache",
        ".pytest_cache",
        "htmlcov",
    }
)

SERVICES_SKIP_SUBPACKAGES = frozenset(
    {
        "chatwoot_service",
        "shopperbot_service",
        "evolution_api_service",
        "vectorstore_service",
        "worldgraph_service",
        "whatsapp_gateway_service",
        "sparkscore_service",
        "creative_engine_service",
        "ifood_service",
        "mcp_service",
        "mlflow_service",
        "event_bus_service",
        "event_consumers",
        "openfinance_gateway_service",
    }
)


def should_skip_tree(parts: tuple[str, ...]) -> bool:
    if any(p in SKIP_DIR_NAMES for p in parts):
        return True
    if len(parts) >= 2 and parts[0] == "services" and parts[1] in SERVICES_SKIP_SUBPACKAGES:
        return True
    return False


def path_ok_for_pattern_scan(rel: Path) -> bool:
    parts = rel.parts
    if "migrations" in parts:
        return False
    if "command_engine" in parts and "handlers" in parts:
        return False
    if rel.name == "registry.py" and "command_engine" in parts:
        return False
    return True


def restrict_framework_roots(rel_parts: tuple[str, ...]) -> bool:
    """True = deve analisar; False = saltar árvore."""
    if not rel_parts:
        return True
    first = rel_parts[0]
    if first in ("agent_core", "command_engine", "app_sinapcore"):
        return True
    if first == "services" and len(rel_parts) == 1:
        return True
    if first == "services" and len(rel_parts) > 1:
        return False
    return False
