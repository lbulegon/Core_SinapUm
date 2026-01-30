"""
Testes de integração do SparkScore (porta 8006).
"""
import pytest
import requests
from tests.services_config import SERVICES

TIMEOUT = 15
config = SERVICES["sparkscore_service"]


def test_sparkscore_health():
    """Health check retorna healthy."""
    resp = requests.get(config["health_url"], timeout=TIMEOUT)
    assert resp.status_code == 200
    data = resp.json()
    assert data.get("status") == "healthy"


def test_sparkscore_analyze_piece_minimal():
    """POST /api/v1/analyze_piece com payload mínimo."""
    payload = {
        "source": "vitrinezap_creative_engine",
        "piece": {
            "piece_id": "int_test_001",
            "piece_type": "image",
            "text_overlay": "PROMO - Chame no WhatsApp",
            "caption": "Compartilhe",
        },
        "objective": {"primary_goal": "whatsapp_click"},
        "distribution": {"channel": "whatsapp_status", "format": "story_vertical"},
    }
    resp = requests.post(config["analyze_url"], json=payload, timeout=TIMEOUT)
    assert resp.status_code == 200
    data = resp.json()
    assert "orbitals" in data
    assert "overall_score" in data
    assert 0 <= data["overall_score"] <= 100
    orbital_ids = [o["orbital_id"] for o in data["orbitals"]]
    assert "csv" in orbital_ids
    assert "semiotic" in orbital_ids


def test_sparkscore_orbital_csv_presente():
    """Orbital CSV está presente na resposta."""
    payload = {
        "source": "vitrinezap_creative_engine",
        "piece": {"piece_id": "csv_test", "piece_type": "image", "text_overlay": "Teste"},
        "objective": {"primary_goal": "whatsapp_click"},
        "distribution": {"channel": "whatsapp_status", "format": "story_vertical"},
    }
    resp = requests.post(config["analyze_url"], json=payload, timeout=TIMEOUT)
    assert resp.status_code == 200
    data = resp.json()
    csv_orb = next((o for o in data["orbitals"] if o["orbital_id"] == "csv"), None)
    assert csv_orb is not None
    assert csv_orb.get("status") == "active"
