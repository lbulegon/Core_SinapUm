"""
Testes MCP Service e iFood Service.
"""
import pytest
import requests
from tests.services_config import SERVICES

TIMEOUT = 10


def test_mcp_health():
    config = SERVICES["mcp_service"]
    try:
        resp = requests.get(config["health_url"], timeout=TIMEOUT)
        assert resp.status_code == 200
    except requests.exceptions.ConnectionError:
        pytest.skip("MCP nao esta rodando")


def test_ifood_health():
    config = SERVICES["ifood_service"]
    try:
        resp = requests.get(config["health_url"], timeout=TIMEOUT)
        assert resp.status_code == 200
    except requests.exceptions.ConnectionError:
        pytest.skip("iFood nao esta rodando")
