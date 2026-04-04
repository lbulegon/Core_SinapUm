"""Serialização JSON do resultado SinapLint."""

from __future__ import annotations

import json
from typing import Any


def dumps(result: dict[str, Any], *, indent: int = 2) -> str:
    return json.dumps(result, indent=indent, ensure_ascii=False)
