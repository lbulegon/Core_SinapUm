"""
Testes de casos de uso - Cenários reais do Creative Engine / VitrineZap
"""

import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.orbitals.pipeline import run_orbitals
from tests.conftest import payload_minimal, payload_full, payload_com_circulacao, payload_sem_cta, payload_texto_longo, payload_vazio

client = TestClient(app)


class TestCasoUsoStoryIdealWhatsApp:
    """Caso: Story otimizada para WhatsApp Status"""

    def test_story_com_cta_hashtag_compartilhe(self):
        payload = payload_minimal(
            text_overlay="50% OFF - Chame no WhatsApp #oferta #promo",
            caption="Compartilhe com seus amigos",
            hashtags=["#oferta", "#promo"],
            channel="whatsapp_status",
            format_type="story_vertical",
        )
        result = run_orbitals(payload)
        csv = next((o for o in result["orbitals"] if o["orbital_id"] == "csv"), None)
        assert csv is not None
        assert csv["status"] == "active"
        assert csv["raw_features"]["circulation_triggers_found"] >= 2
        assert csv["raw_features"]["channel_circulation_fit"] >= 0.8
        assert csv["score"] >= 70


class TestCasoUsoPeçaSemCTA:
    """Caso: Peça sem Call-to-Action explícito"""

    def test_insight_cta_ausente_para_whatsapp(self):
        payload = payload_minimal(
            text_overlay="PROMOÇÃO",
            caption="Aproveite nossa oferta",
        )
        result = run_orbitals(payload)
        insights = result.get("insights", [])
        cta_insights = [i for i in insights if "CTA" in i.get("title", "")]
        assert len(cta_insights) >= 1


class TestCasoUsoTextoExcessivo:
    """Caso: Peça com texto muito longo"""

    def test_csv_detecta_obstaculo(self):
        texto = " ".join(["palavra"] * 55)  # >50 palavras = alto obstacle
        payload = payload_minimal(text_overlay=texto, caption="")
        result = run_orbitals(payload)
        csv = next((o for o in result["orbitals"] if o["orbital_id"] == "csv"), None)
        assert csv is not None
        assert csv["raw_features"]["obstacle_score"] > 0.2


class TestCasoUsoViaAPI:
    """Casos de uso via endpoint HTTP"""

    def test_analyze_piece_retorna_csv(self):
        payload = payload_minimal(
            text_overlay="Compartilhe - Chame #oferta",
        )
        resp = client.post("/api/v1/analyze_piece", json=payload)
        assert resp.status_code == 200
        data = resp.json()
        orbital_ids = [o["orbital_id"] for o in data["orbitals"]]
        assert "csv" in orbital_ids

    def test_overall_score_range(self):
        payload = payload_full()
        resp = client.post("/api/v1/analyze_piece", json=payload)
        assert resp.status_code == 200
        data = resp.json()
        assert 0 <= data["overall_score"] <= 100

    def test_payload_vazio_retorna_200(self):
        payload = payload_minimal(text_overlay="", caption="")
        resp = client.post("/api/v1/analyze_piece", json=payload)
        assert resp.status_code == 200
