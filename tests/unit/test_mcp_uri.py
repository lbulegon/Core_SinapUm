"""
Testes unitários do parser e validação de URIs sinap:// (MCP Resources).
PR5 — Hardening + testes.
"""
import pytest
import sys
from pathlib import Path
_root = Path(__file__).resolve().parents[2]
if str(_root) not in sys.path:
    sys.path.insert(0, str(_root))

from mcp.uri import parse_sinap_uri, validate_sinap_uri, is_sinap_uri, SinapURI


class TestParseSinapUri:
    def test_parse_valid_uri_with_id(self):
        u = parse_sinap_uri("sinap://vitrinezap/catalog/123")
        assert u is not None
        assert u.vertical == "vitrinezap"
        assert u.entity == "catalog"
        assert u.id == "123"

    def test_parse_valid_uri_without_id(self):
        u = parse_sinap_uri("sinap://vitrinezap/catalog")
        assert u is not None
        assert u.vertical == "vitrinezap"
        assert u.entity == "catalog"
        assert u.id is None

    def test_parse_invalid_returns_none(self):
        assert parse_sinap_uri("") is None
        assert parse_sinap_uri("http://other.com/x") is None
        assert parse_sinap_uri("sinap:/missing/slash") is None

    def test_parse_with_query(self):
        u = parse_sinap_uri("sinap://motopro/orders?limit=10")
        assert u is not None
        assert u.entity == "orders"
        assert u.query is not None
        assert u.query.get("limit") == "10"


class TestValidateSinapUri:
    def test_valid_known_vertical_entity(self):
        assert validate_sinap_uri("sinap://vitrinezap/catalog/1") is True
        assert validate_sinap_uri("sinap://motopro/orders") is True

    def test_invalid_uri_returns_false(self):
        assert validate_sinap_uri("http://x.com") is False
        assert validate_sinap_uri("sinap://unknown_vertical/x") is False


class TestIsSinapUri:
    def test_true_for_valid(self):
        assert is_sinap_uri("sinap://vitrinezap/catalog/1") is True

    def test_false_for_other(self):
        assert is_sinap_uri("https://example.com") is False
