"""
Executa análise na ref base (git worktree) e junta ``delta`` ao resultado atual.
"""

from __future__ import annotations

import shutil
import subprocess
import tempfile
from pathlib import Path
from typing import Any

from app_sinaplint.engine.delta import enrich_head_with_delta, get_changed_files
from app_sinaplint.engine.orchestrator import SinapLintOrchestrator


def _is_git_repo(root: Path) -> bool:
    p = subprocess.run(
        ["git", "-C", str(root), "rev-parse", "--is-inside-work-tree"],
        capture_output=True,
        text=True,
    )
    return p.returncode == 0 and "true" in (p.stdout or "").lower()


def _resolve_remote_ref(root: Path, base: str) -> str | None:
    """Normaliza para ``origin/<branch>`` quando possível."""
    b = base.strip()
    if not b:
        return None
    if b.startswith("refs/"):
        return b
    if "/" in b and not b.startswith("origin/"):
        return b
    subprocess.run(
        ["git", "-C", str(root), "fetch", "--depth", "1", "origin", b],
        capture_output=True,
        check=False,
    )
    return f"origin/{b}"


def run_check_with_delta(root: Path, base_ref: str) -> dict[str, Any]:
    """
    Corre o orquestrador em ``root`` e, se possível, num worktree de ``base_ref``,
    e acrescenta ``delta`` + ``delta_summary`` ao resultado.
    """
    root = root.resolve()
    current = SinapLintOrchestrator().run(root)

    if not base_ref.strip() or not _is_git_repo(root):
        current["delta"] = {"base_available": False, "reason": "not_git_or_no_base"}
        current["delta_summary"] = ""
        return current

    remote_ref = _resolve_remote_ref(root, base_ref)
    if not remote_ref:
        current["delta"] = {"base_available": False, "reason": "invalid_base_ref"}
        current["delta_summary"] = ""
        return current

    wt = tempfile.mkdtemp(prefix="sinaplint-base-")
    try:
        proc = subprocess.run(
            ["git", "-C", str(root), "worktree", "add", "--detach", wt, remote_ref],
            capture_output=True,
            text=True,
        )
        if proc.returncode != 0:
            current["delta"] = {
                "base_available": False,
                "reason": "worktree_failed",
                "detail": (proc.stderr or proc.stdout or "")[:500],
            }
            current["delta_summary"] = ""
            return current

        base_result = SinapLintOrchestrator().run(Path(wt))
    finally:
        subprocess.run(
            ["git", "-C", str(root), "worktree", "remove", "-f", wt],
            capture_output=True,
            check=False,
        )
        if Path(wt).exists():
            shutil.rmtree(wt, ignore_errors=True)

    current = enrich_head_with_delta(
        current,
        base_result,
        base_ref=base_ref,
        resolved_ref=remote_ref,
    )
    delta = current.get("delta") or {}
    changed = get_changed_files(root, remote_ref)
    if changed:
        delta["changed_files_count"] = len(changed)
        delta["changed_files"] = changed[:400]
        current["delta"] = delta
    return current
