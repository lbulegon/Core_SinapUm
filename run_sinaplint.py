#!/usr/bin/env python3
"""
Compatibilidade: delega para o CLI SinapLint (`app_sinaplint`).

Preferir: python sinaplint.py check | python -m app_sinaplint check
"""

from __future__ import annotations

import sys
from pathlib import Path

_root = Path(__file__).resolve().parent
if str(_root) not in sys.path:
    sys.path.insert(0, str(_root))

from app_sinaplint.cli import main

if __name__ == "__main__":
    argv = list(sys.argv[1:])
    if not argv:
        argv = ["check"]
    elif argv[0] not in ("check", "fix"):
        argv = ["check"] + argv
    raise SystemExit(main(argv))
