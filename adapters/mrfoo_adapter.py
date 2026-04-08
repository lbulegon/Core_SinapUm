"""
Adapter MrFoo — Food Knowledge Graph (FKG) e recursos sinap://mrfoo/*.
Implementado: chama API do MrFoo (HTTP) com MRFOO_BASE_URL e MRFOO_API_TOKEN.
Contexto tenant: header X-Tenant-ID (padrão documentado).
"""
import logging
import os
from typing import Any, Dict, List, Optional

import requests

from .base import BaseAdapter

logger = logging.getLogger(__name__)

MRFOO_BASE_URL = os.environ.get("MRFOO_BASE_URL", "").rstrip("/")
MRFOO_API_TOKEN = os.environ.get("MRFOO_API_TOKEN", "")


def _headers(tenant_id: Optional[str] = None) -> Dict[str, str]:
    h = {"Content-Type": "application/json"}
    if MRFOO_API_TOKEN:
        h["Authorization"] = f"Bearer {MRFOO_API_TOKEN}"
    if tenant_id:
        h["X-Tenant-ID"] = str(tenant_id)
    return h


def _get(path: str, params: Optional[Dict[str, Any]] = None, tenant_id: Optional[str] = None) -> Dict[str, Any]:
    if not MRFOO_BASE_URL:
        return {"success": False, "error": "MRFOO_BASE_URL not configured"}
    url = f"{MRFOO_BASE_URL}{path}"
    try:
        r = requests.get(url, params=params or {}, headers=_headers(tenant_id), timeout=30)
        r.raise_for_status()
        return r.json() if r.content else {}
    except requests.RequestException as e:
        logger.warning("MrFoo GET %s: %s", path, e)
        return {"success": False, "error": str(e)}


def _post(path: str, json: Optional[Dict] = None, tenant_id: Optional[str] = None) -> Dict[str, Any]:
    if not MRFOO_BASE_URL:
        return {"success": False, "error": "MRFOO_BASE_URL not configured"}
    url = f"{MRFOO_BASE_URL}{path}"
    try:
        r = requests.post(url, json=json or {}, headers=_headers(tenant_id), timeout=60)
        r.raise_for_status()
        return r.json() if r.content else {}
    except requests.RequestException as e:
        logger.warning("MrFoo POST %s: %s", path, e)
        return {"success": False, "error": str(e)}


def graph_status(tenant_id: str) -> Dict[str, Any]:
    """GET /api/v1/graph/status/ — status do grafo + health Neo4j."""
    out = _get("/api/v1/graph/status/", tenant_id=tenant_id)
    out.setdefault("success", "error" not in out)
    return out


def graph_sync_full(tenant_id: str) -> Dict[str, Any]:
    """POST /api/v1/graph/sync/full/ — sync completo Postgres → Neo4j."""
    out = _post("/api/v1/graph/sync/full/", tenant_id=tenant_id)
    out.setdefault("success", "error" not in out)
    return out


def graph_sync_incremental(tenant_id: str) -> Dict[str, Any]:
    """POST /api/v1/graph/sync/incremental/ — sync incremental."""
    out = _post("/api/v1/graph/sync/incremental/", tenant_id=tenant_id)
    out.setdefault("success", "error" not in out)
    return out


def margin_per_minute(tenant_id: str, timeslot: Optional[str] = None) -> Dict[str, Any]:
    """GET /api/v1/graph/insights/margin-per-minute/?timeslot=..."""
    params = {}
    if timeslot:
        params["timeslot"] = timeslot
    return _get("/api/v1/graph/insights/margin-per-minute/", params=params or None, tenant_id=tenant_id)


def complexity_score(tenant_id: str) -> Dict[str, Any]:
    """GET /api/v1/graph/insights/complexity/."""
    return _get("/api/v1/graph/insights/complexity/", tenant_id=tenant_id)


def combo_suggestions(tenant_id: str, timeslot: Optional[str] = None) -> Dict[str, Any]:
    """GET /api/v1/graph/insights/combos/?timeslot=..."""
    params = {}
    if timeslot:
        params["timeslot"] = timeslot
    return _get("/api/v1/graph/insights/combos/", params=params or None, tenant_id=tenant_id)


def new_item_suggestions(tenant_id: str, max_items: int = 10) -> Dict[str, Any]:
    """GET /api/v1/graph/insights/new-items/?max=..."""
    return _get("/api/v1/graph/insights/new-items/", params={"max": max_items}, tenant_id=tenant_id)


def triangle_metrics(tenant_id: str, timeslot: Optional[str] = None) -> Dict[str, Any]:
    """GET /api/v1/graph/insights/triangle/?timeslot=..."""
    params = {}
    if timeslot:
        params["timeslot"] = timeslot
    return _get("/api/v1/graph/insights/triangle/", params=params or None, tenant_id=tenant_id)


# -----------------------------------------------------------------------------
# BaseAdapter: get/list para sinap://mrfoo/graph/...
# -----------------------------------------------------------------------------


class MrFooAdapter(BaseAdapter):
    """Adapter para Resources sinap://mrfoo/* (menu, graph/status, graph/insights/...)."""

    def get(
        self,
        entity: str,
        id: Optional[str] = None,
        query: Optional[Dict[str, str]] = None,
    ) -> Optional[Dict[str, Any]]:
        query = query or {}
        tenant_id = query.get("tenant_id", "").strip()
        if not tenant_id:
            return None
        if entity == "menu" and id:
            # Legado: menu por id (pode chamar endpoint futuro)
            out = get_menu(id, tenant_id=tenant_id)
            return out if out.get("success") else None
        if entity == "graph" and id == "status":
            out = graph_status(tenant_id)
            return out if out.get("success") else None
        if entity == "graph" and id and id.startswith("insights/"):
            sub = id.replace("insights/", "", 1)
            if sub == "margin_per_minute":
                out = margin_per_minute(tenant_id, query.get("timeslot"))
            elif sub == "complexity":
                out = complexity_score(tenant_id)
            elif sub == "combos":
                out = combo_suggestions(tenant_id, query.get("timeslot"))
            elif sub == "new_items":
                max_items = int(query.get("max", "10") or "10")
                out = new_item_suggestions(tenant_id, max_items)
            else:
                return None
            return out if out.get("success") else None
        return None

    def list(self, entity: str, query: Optional[Dict[str, str]] = None) -> Optional[Dict[str, Any]]:
        return None

    def normalizar_produto_cardapio(self, raw: Dict[str, Any]) -> Dict[str, Any]:
        preco = float(raw.get("preco", 0.0) or 0.0)
        cmv = float(raw.get("cmv", 0.0) or 0.0)
        cmv_percentual = raw.get("cmv_percentual", None)
        if cmv_percentual is None or cmv_percentual == "":
            cmv_percentual = (cmv / preco) if preco > 0 else 0.0

        return {
            "produto": str(raw.get("produto") or "").strip() or "PRODUTO_SEM_NOME",
            "cmv": cmv,
            "preco": preco,
            "vendas": int(float(raw.get("vendas", 0) or 0)),
            "receita": float(raw.get("receita", 0.0) or 0.0),
            "cmv_percentual": float(cmv_percentual or 0.0),
            "tempo_preparo": float(raw.get("tempo_preparo", 1.0) or 1.0),
            "etapas": float(raw.get("etapas", 1.0) or 1.0),
            "ingredientes": float(raw.get("ingredientes", 1.0) or 1.0),
        }

    def analisar_cardapio(self, produtos: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Bridge MrFoo -> Core command_engine (execução inline via handler oficial).
        Evita acoplamento de domínio no orbital.
        """
        from command_engine.handlers.menu.analisar_cardapio import execute_inline

        normalizados = [self.normalizar_produto_cardapio(p or {}) for p in (produtos or [])]
        return execute_inline(normalizados, source="mrfoo_adapter")


def get_menu(menu_id: str, tenant_id: Optional[str] = None) -> Dict[str, Any]:
    """Obtém cardápio por id (stub ou endpoint futuro)."""
    # Se MrFoo expuser GET /api/v1/menu/<id>/ com tenant, usar _get
    if MRFOO_BASE_URL and tenant_id:
        return _get(f"/api/v1/menu/{menu_id}/", tenant_id=tenant_id)
    return {"success": False, "menu": None, "error": "MrFoo adapter: tenant_id or MRFOO_BASE_URL missing"}


def get_shopping_list(tenant_id: Optional[str] = None, **kwargs: Any) -> Dict[str, Any]:
    """Lista de compras (stub ou endpoint futuro)."""
    if MRFOO_BASE_URL and tenant_id:
        return _get("/api/compras/listas/", tenant_id=tenant_id)
    return {"success": False, "error": "MrFoo adapter not configured"}
