"""
Testes de integração do ShopperBot Service (porta 7030).
"""

import pytest
import requests
from tests.services_config import SERVICES

TIMEOUT = 10
config = SERVICES["shopperbot_service"]


def test_shopperbot_health():
    """Health retorna 200."""
    resp = requests.get(config["health_url"], timeout=TIMEOUT)
    assert resp.status_code == 200
    data = resp.json()
    assert "status" in data or "healthy" in str(data).lower()


def test_shopperbot_intent_classify():
    """POST /v1/intent/classify com payload válido."""
    url = f"{config['root_url']}v1/intent/classify"
    payload = {
        "message": "Quero ver produtos",
        "contexto": "group",
        "user_id": "test_user",
        "estabelecimento_id": "est_test",
    }
    resp = requests.post(url, json=payload, timeout=TIMEOUT)
    assert resp.status_code == 200, f"Esperado 200, obtido {resp.status_code}"
    data = resp.json()
    assert "intent" in data
    assert "confidence" in data
