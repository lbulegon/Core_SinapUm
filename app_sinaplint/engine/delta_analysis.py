"""
Compatibilidade: reexporta o pacote ``engine.delta`` (localização antiga).
"""

from __future__ import annotations

from app_sinaplint.engine.delta import (
    DeltaAnalyzer,
    compute_delta,
    enrich_head_with_delta,
    format_delta_summary,
    generate_pr_comment,
    get_changed_files,
    summarize_delta,
)
from app_sinaplint.engine.delta.blocking import (
    DeltaBlocker,
    format_blocking_message,
    load_blocking_rules,
)

__all__ = [
    "DeltaAnalyzer",
    "DeltaBlocker",
    "compute_delta",
    "enrich_head_with_delta",
    "format_blocking_message",
    "format_delta_summary",
    "generate_pr_comment",
    "get_changed_files",
    "load_blocking_rules",
    "summarize_delta",
]
