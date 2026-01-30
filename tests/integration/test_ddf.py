"""
Testes de integração do DDF Service (porta 8005).
"""
import pytest
import requests
from tests.services_config import SERVICES

TIMEOUT = 10
config = SERVICES["ddf_service"]


def test_ddf_health():
    """Health retorna healthy."""
    resp = requests.get(config["health_url"], timeout=TIMEOUT)
    assert resp.status_code == 200
    data = resp.json()
    assert data.get("status") == "healthy"
    assert "DDF" in str(data.get("service", ""))


def test_ddf_root():
    """Root retorna info do serviço."""
    resp = requests.get(config["root_url"], timeout=TIMEOUT)
    assert resp.status_code == 200
    data = resp.json()
    assert data.get("status") == "online"


def test_ddf_detect():
    """POST /ddf/detect detecta categoria."""
    url = f"{config['root_url']}ddf/detect"
    payload = {"text": "gerar uma imagem de um gato", "context": {}}
    resp = requests.post(url, json=payload, timeout=TIMEOUT)
    assert resp.status_code == 200
    data = resp.json()
    assert data.get("success") is True
    assert "detection" in data
