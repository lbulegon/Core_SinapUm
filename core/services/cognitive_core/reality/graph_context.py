"""
WorldGraph / Neo4j — consulta estrutural (Segundidade relacional), sem misturar com RAG.
"""
from __future__ import annotations

import json
import logging
import os
from typing import Any, Dict, List, Optional

import requests

logger = logging.getLogger(__name__)


def _bolt_config() -> Dict[str, str]:
    return {
        "url": (os.getenv("WORLDGRAPH_BOLT_URL") or "").strip(),
        "user": (
            os.getenv("WORLDGRAPH_USER") or os.getenv("WORLDGRAPH_NEO4J_USER") or "neo4j"
        ).strip(),
        "password": (os.getenv("WORLDGRAPH_PASSWORD") or os.getenv("WORLDGRAPH_NEO4J_PASSWORD") or "").strip(),
    }


def _http_graph_url() -> str:
    return (os.getenv("WORLDGRAPH_HTTP_URL") or "").strip().rstrip("/")


def _run_neo4j_bolt(cypher: str, params: Dict[str, Any]) -> List[Dict[str, Any]]:
    try:
        from neo4j import GraphDatabase
    except ImportError:
        logger.debug("neo4j driver not installed; skip bolt query")
        return []

    cfg = _bolt_config()
    if not cfg["url"] or not cfg["password"]:
        return []

    driver = GraphDatabase.driver(cfg["url"], auth=(cfg["user"], cfg["password"]))
    rows: List[Dict[str, Any]] = []
    try:
        with driver.session() as session:
            result = session.run(cypher, params)
            for record in result:
                rows.append(record.data())
    finally:
        driver.close()
    return rows


def _run_http_graph(cypher: str, params: Dict[str, Any]) -> Dict[str, Any]:
    base = _http_graph_url()
    if not base:
        return {}
    try:
        r = requests.post(
            f"{base}/cypher",
            json={"query": cypher, "params": params},
            timeout=float(os.getenv("WORLDGRAPH_HTTP_TIMEOUT", "8")),
            headers={"Content-Type": "application/json"},
        )
        if r.status_code >= 400:
            return {"error": r.text[:500], "status_code": r.status_code}
        return r.json() if r.content else {}
    except Exception as e:
        logger.warning("WORLDGRAPH_HTTP_URL request failed: %s", e)
        return {"error": str(e)}


def fetch_graph_context(
    *,
    cypher: Optional[str] = None,
    params: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """
    Consulta best-effort: Bolt (neo4j driver) ou microserviço HTTP WORLDGRAPH_HTTP_URL.
    """
    params = params or {}
    bolt = _bolt_config()["url"]
    http_base = _http_graph_url()

    if not cypher:
        cypher = (os.getenv("WORLDGRAPH_DEFAULT_CYPHER") or "").strip()

    if not cypher:
        if bolt:
            return {
                "available": True,
                "stub": True,
                "bolt_configured": True,
                "rows": [],
                "note": "Set WORLDGRAPH_DEFAULT_CYPHER or pass cypher from caller.",
            }
        if http_base:
            return {"available": True, "stub": True, "http_configured": True, "rows": []}
        return {"available": False, "reason": "No WORLDGRAPH_BOLT_URL / WORLDGRAPH_HTTP_URL", "rows": []}

    if http_base and os.getenv("WORLDGRAPH_PREFER_HTTP", "").lower() in ("1", "true", "yes"):
        data = _run_http_graph(cypher, params)
        return {
            "available": True,
            "via": "http",
            "rows": data.get("rows") if isinstance(data, dict) else data,
            "raw": data,
        }

    rows = _run_neo4j_bolt(cypher, params)
    if rows is not None and rows != []:
        return {"available": True, "via": "bolt", "rows": rows, "stub": False}

    if http_base:
        data = _run_http_graph(cypher, params)
        return {
            "available": True,
            "via": "http_fallback",
            "rows": (data.get("rows") if isinstance(data, dict) else []) or [],
            "raw": data,
        }

    return {
        "available": bool(bolt),
        "stub": True,
        "rows": [],
        "note": "Cypher configured but no successful backend (install neo4j driver or HTTP gateway).",
    }


def graph_snippet_for_tenant(tenant_id: str) -> Dict[str, Any]:
    """
    Subgraço / métricas por tenant. Usa WORLDGRAPH_TENANT_CYPHER se definido; senão tenta default + $tenant.
    """
    tid = (tenant_id or "").strip()
    template = (os.getenv("WORLDGRAPH_TENANT_CYPHER") or "").strip()
    if template:
        return fetch_graph_context(cypher=template, params={"tenant": tid, "tenant_id": tid})

    default = (os.getenv("WORLDGRAPH_DEFAULT_CYPHER") or "").strip()
    if default:
        return fetch_graph_context(cypher=default, params={"tenant": tid, "tenant_id": tid})

    # Sem query configurada: retorno mínimo com tenant para depuração
    base = fetch_graph_context()
    base["tenant_id"] = tid
    base["graph_mode"] = "unconfigured_queries"
    return base
