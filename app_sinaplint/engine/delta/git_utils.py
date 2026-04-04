"""
Utilitários Git para delta (ficheiros alterados entre base e HEAD).
"""

from __future__ import annotations

import subprocess
from pathlib import Path


def get_changed_files(root: Path | str, base_ref: str = "origin/main") -> list[str]:
    """
    Lista ficheiros diferentes entre ``base_ref`` e ``HEAD`` (intervalo de merge ``...``).

    Em PRs costuma corresponder ao conjunto de alterações introduzidas na branch.
    """
    root = Path(root).resolve()
    b = (base_ref or "").strip()
    if not b:
        return []
    try:
        result = subprocess.run(
            ["git", "-C", str(root), "diff", "--name-only", f"{b}...HEAD"],
            capture_output=True,
            text=True,
            timeout=120,
        )
        if result.returncode != 0:
            return []
        return [f.strip() for f in (result.stdout or "").splitlines() if f.strip()]
    except (OSError, subprocess.SubprocessError):
        return []
