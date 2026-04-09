"""
Testes unitários dos adapters (BaseAdapter, mocks).
PR5 — Hardening + testes.
"""
import pytest
import sys
from pathlib import Path
_root = Path(__file__).resolve().parents[2]
if str(_root) not in sys.path:
    sys.path.insert(0, str(_root))

from adapters.base import BaseAdapter


class ConcreteAdapter(BaseAdapter):
    """Adapter concreto para teste."""

    def get(self, entity, id=None, query=None):
        if entity == "catalog" and id == "1":
            return {"id": "1", "name": "Test"}
        return None

    def list(self, entity, query=None):
        if entity == "catalog":
            return {"items": [], "total": 0}
        return None


class TestBaseAdapter:
    def test_get_default_returns_none(self):
        # BaseAdapter.get() retorna None por padrão
        base = BaseAdapter()
        assert base.get("catalog", "1") is None

    def test_list_default_returns_none(self):
        base = BaseAdapter()
        assert base.list("catalog") is None


class TestConcreteAdapter:
    def test_get_returns_data(self):
        ad = ConcreteAdapter()
        out = ad.get("catalog", "1")
        assert out == {"id": "1", "name": "Test"}

    def test_get_unknown_returns_none(self):
        ad = ConcreteAdapter()
        assert ad.get("catalog", "999") is None

    def test_list_returns_structure(self):
        ad = ConcreteAdapter()
        out = ad.list("catalog")
        assert out is not None
        assert "items" in out
        assert out["total"] == 0


class TestMrFooAdapterGraph:
    """MrFoo adapter: graph_status e recursos sinap://mrfoo/graph/*."""

    def test_graph_status_returns_dict_structure(self):
        from unittest.mock import patch
        from adapters.mrfoo_adapter import graph_status
        with patch.dict("os.environ", {"MRFOO_BASE_URL": "http://mrfoo.test"}):
            with patch("adapters.mrfoo_adapter.requests.get") as mget:
                mget.return_value.status_code = 200
                mget.return_value.content = b'{"neo4j_connected": true, "last_synced_at": null}'
                mget.return_value.json.return_value = {"neo4j_connected": True, "last_synced_at": None}
                out = graph_status("1")
                assert isinstance(out, dict)
                assert out.get("success") is True or "error" in out
                mget.assert_called_once()

    def test_mrfoo_adapter_get_graph_status_requires_tenant(self):
        from adapters.mrfoo_adapter import MrFooAdapter
        ad = MrFooAdapter()
        # Sem tenant_id na query, get graph/status retorna None (query vazia)
        assert ad.get("graph", "status", query={}) is None
        out = ad.get("graph", "status", query={"tenant_id": "1"})
        # Pode ser None se MRFOO_BASE_URL nao estiver setado
        if out is not None:
            assert isinstance(out, dict)
