"""Saída legível para terminal."""

from __future__ import annotations

import sys
from typing import Any, Optional, TextIO


def print_report(result: dict[str, Any], stream: Optional[TextIO] = None) -> None:
    out = stream or sys.stdout
    out.write("SinapLint — relatório\n")
    out.write("=" * 48 + "\n")
    out.write(f"Score: {result['score']}/100  ({result['quality']})  PASS={result['ok']}\n\n")

    st = result.get("structure") or {}
    out.write("Estrutura\n")
    for name, ok in st.get("dirs_ok", []):
        out.write(f"  [{'OK' if ok else '--'}] dir  {name}\n")
    for name, ok in st.get("files_ok", []):
        out.write(f"  [{'OK' if ok else '--'}] file {name}\n")
    for e in st.get("errors", []):
        out.write(f"  [!!] {e}\n")

    out.write("\nMódulos orbitais\n")
    for m in result.get("modules", []):
        out.write(f"  {m['module']}: penalty={m['penalty']} missing={m.get('missing')}\n")

    out.write("\nPadrões (regex)\n")
    for i in result.get("pattern_issues", []):
        out.write(f"  {i['path']} → {i['message']}\n")
    if result.get("suggestions"):
        out.write("\nSugestões\n")
        for s in result["suggestions"]:
            out.write(f"  • {s['problem']}: {s['suggestion']}\n")

    out.write("\nAST\n")
    for i in result.get("ast_issues", []):
        out.write(f"  {i['path']} → {i['message']}\n")

    out.write("\n" + "=" * 48 + "\n")
