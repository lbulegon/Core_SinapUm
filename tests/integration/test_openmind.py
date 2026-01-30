"""
Testes de integração do OpenMind AI (porta 8001).
"""
import pytest
import requests
from tests.services_config import SERVICES

TIMEOUT = 10
config = SERVICES["openmind"]


def test_openmind_health():
    """Health retorna healthy."""
    resp = requests.get(config["health_url"], timeout=TIMEOUT)
    assert resp.status_code == 200
    data = resp.json()
    assert data.get("status") == "healthy"
    assert "OpenMind" in str(data.get("service", ""))


def test_openmind_root():
    """Root retorna info do serviço."""
    resp = requests.get(config["root_url"], timeout=TIMEOUT)
    assert resp.status_code == 200
    data = resp.json()
    assert "service" in data
    assert "/docs" in str(data.get("docs", ""))
