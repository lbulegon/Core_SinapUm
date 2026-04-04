"""
Constrói o grafo dirigido de dependências entre pastas ``app_*`` na raiz do monólito.

Usa AST (não regex) para imports absolutos ``app_*`` — mesma semântica que o resto do motor.
"""

from __future__ import annotations

import ast
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

SKIP_SUBDIR_NAMES = frozenset(
    {
        "migrations",
        "__pycache__",
        ".venv",
        "venv",
        "node_modules",
        "htmlcov",
        ".pytest_cache",
        ".git",
    }
)


def find_django_apps(root: Path) -> list[str]:
    if not root.is_dir():
        return []
    out: list[str] = []
    try:
        for p in sorted(root.iterdir()):
            if p.is_dir() and p.name.startswith("app_") and not p.name.startswith("."):
                out.append(p.name)
    except OSError:
        return []
    return out


def _iter_app_py_files(app_root: Path) -> list[Path]:
    files: list[Path] = []
    try:
        for py in app_root.rglob("*.py"):
            if any(part in SKIP_SUBDIR_NAMES for part in py.parts):
                continue
            files.append(py)
    except OSError:
        return []
    return files


def _imports_app_modules(py_file: Path) -> set[str]:
    try:
        src = py_file.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        return set()
    try:
        tree = ast.parse(src, filename=str(py_file))
    except SyntaxError:
        return set()
    found: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                root_mod = alias.name.split(".")[0]
                if root_mod.startswith("app_"):
                    found.add(root_mod)
        elif isinstance(node, ast.ImportFrom) and node.module:
            if getattr(node, "level", 0) and node.level > 0:
                continue
            root_mod = node.module.split(".")[0]
            if root_mod.startswith("app_"):
                found.add(root_mod)
    return found


def build_adjacency_and_edges(
    root: Path, django_apps: list[str]
) -> tuple[dict[str, set[str]], list[dict[str, Any]], dict[str, int]]:
    """Adjacência (sets), arestas pesadas e fan-in."""
    app_set = set(django_apps)
    if not app_set:
        return {}, [], {}

    pair_file_hits: dict[tuple[str, str], set[str]] = defaultdict(set)

    for app in django_apps:
        app_dir = root / app
        if not app_dir.is_dir():
            continue
        for py in _iter_app_py_files(app_dir):
            try:
                rel = str(py.relative_to(root))
            except ValueError:
                rel = str(py)
            targets = _imports_app_modules(py)
            for tgt in targets:
                if tgt == app or tgt not in app_set:
                    continue
                pair_file_hits[(app, tgt)].add(rel)

    adj: dict[str, set[str]] = defaultdict(set)
    edges: list[dict[str, Any]] = []
    for (src, dst), files in sorted(pair_file_hits.items()):
        w = len(files)
        adj[src].add(dst)
        edges.append(
            {
                "from": src,
                "to": dst,
                "weight": w,
                "files_sample": sorted(files)[:8],
            }
        )

    fan_in: dict[str, int] = Counter()
    for e in edges:
        fan_in[e["to"]] += e["weight"]
    return dict(adj), edges, dict(fan_in)


class DjangoAppGraph:
    """Descobre ``app_*`` e constrói o grafo dirigido de dependências."""

    def __init__(self, root_path: Path | str) -> None:
        self.root_path = Path(root_path).resolve()
        self.apps: list[str] = []
        self._adj: dict[str, set[str]] = {}
        self._edges: list[dict[str, Any]] = []
        self._fan_in: dict[str, int] = {}

    def build(self) -> dict[str, Any]:
        self.apps = find_django_apps(self.root_path)
        self._adj, self._edges, self._fan_in = build_adjacency_and_edges(
            self.root_path, self.apps
        )
        # Apps isolados aparecem com lista vazia
        graph: dict[str, list[str]] = {}
        for a in self.apps:
            graph[a] = sorted(self._adj.get(a, set()))
        for a in sorted(self._adj.keys()):
            if a not in graph:
                graph[a] = sorted(self._adj[a])
        return {
            "apps": list(self.apps),
            "graph": graph,
            "edges": list(self._edges),
            "fan_in": dict(self._fan_in),
        }
