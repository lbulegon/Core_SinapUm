from __future__ import annotations

from typing import Any, NotRequired, TypedDict


class SinapContext(TypedDict, total=False):
    estabelecimento_id: NotRequired[int | str]
    trace_id: NotRequired[str]


def merge_context(*parts: dict[str, Any] | None) -> dict[str, Any]:
    out: dict[str, Any] = {}
    for p in parts:
        if p:
            out.update(p)
    return out
