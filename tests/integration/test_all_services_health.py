"""
Testes de health check para todos os serviços do Core_SinapUm.
Exige: docker compose up (serviços rodando).
"""
import pytest
import requests
from tests.services_config import SERVICES

TIMEOUT = 10


def test_web_health():
    config = SERVICES["web"]
    resp = requests.get(config["health_url"], timeout=TIMEOUT)
    assert resp.status_code == 200


def test_openmind_health():
    config = SERVICES["openmind"]
    resp = requests.get(config["health_url"], timeout=TIMEOUT)
    assert resp.status_code == 200


def test_ddf_health():
    config = SERVICES["ddf_service"]
    resp = requests.get(config["health_url"], timeout=TIMEOUT)
    assert resp.status_code == 200


def test_sparkscore_health():
    config = SERVICES["sparkscore_service"]
    resp = requests.get(config["health_url"], timeout=TIMEOUT)
    assert resp.status_code == 200


def test_shopperbot_health():
    config = SERVICES["shopperbot_service"]
    resp = requests.get(config["health_url"], timeout=TIMEOUT)
    assert resp.status_code == 200


def test_mcp_health():
    config = SERVICES["mcp_service"]
    try:
        resp = requests.get(config["health_url"], timeout=TIMEOUT)
        assert resp.status_code == 200
    except requests.exceptions.ConnectionError:
        pytest.skip("MCP Service nao esta rodando")


def test_ifood_health():
    config = SERVICES["ifood_service"]
    try:
        resp = requests.get(config["health_url"], timeout=TIMEOUT)
        assert resp.status_code == 200
    except requests.exceptions.ConnectionError:
        pytest.skip("iFood Service nao esta rodando")
