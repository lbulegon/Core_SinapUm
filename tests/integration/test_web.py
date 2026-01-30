"""
Testes de integração do Core Web (Django, porta 5000).
"""

import pytest
import requests
from tests.services_config import SERVICES

TIMEOUT = 10
config = SERVICES["web"]


def test_web_health():
    """Health check retorna 200."""
    resp = requests.get(config["health_url"], timeout=TIMEOUT)
    assert resp.status_code == 200


def test_web_root():
    """Root retorna 200 (página principal ou redirect)."""
    resp = requests.get(config["root_url"], timeout=TIMEOUT, allow_redirects=True)
    assert resp.status_code == 200


def test_web_admin_accessible():
    """Admin está acessível (pode redirecionar para login)."""
    resp = requests.get(f"{config['root_url']}admin/", timeout=TIMEOUT, allow_redirects=True)
    assert resp.status_code in [200, 302]
