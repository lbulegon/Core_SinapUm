"""
Pacote delta: comparação baseline vs HEAD, Git helpers e formatação de PR.
"""

from __future__ import annotations

from app_sinaplint.engine.delta.blocking import (
    DeltaBlocker,
    format_blocking_message,
    load_blocking_rules,
)
from app_sinaplint.engine.delta.comment_formatter import generate_pr_comment
from app_sinaplint.engine.delta.delta_analyzer import (
    DeltaAnalyzer,
    compute_delta,
    enrich_head_with_delta,
)
from app_sinaplint.engine.delta.delta_formatter import format_delta_summary, summarize_delta
from app_sinaplint.engine.delta.git_utils import get_changed_files

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
