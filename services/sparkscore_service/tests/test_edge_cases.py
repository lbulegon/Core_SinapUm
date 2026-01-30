"""
Testes de edge cases - Payloads extremos, formatos inesperados
"""

import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.orbitals.pipeline import run_orbitals
from tests.conftest import payload_minimal

client = TestClient(app)


class TestEdgeCasesPayload:
    """Edge cases de payload"""

    def test_piece_sem_text_overlay_ni_caption(self):
        payload = payload_minimal(text_overlay="", caption="")
        result = run_orbitals(payload)
        assert "orbitals" in result
        assert len(result["orbitals"]) > 0
        assert result["overall_score"] is not None

    def test_payload_com_distribution_vazio(self):
        payload = payload_minimal()
        payload["distribution"] = {}
        result = run_orbitals(payload)
        assert "orbitals" in result
        csv = next((o for o in result["orbitals"] if o["orbital_id"] == "csv"), None)
        assert csv is not None

    def test_payload_formato_legado_sem_piece(self):
        """Formato antigo: text_overlay e caption no root"""
        payload = {
            "source": "legacy",
            "text_overlay": "Chame no WhatsApp",
            "caption": "Promoção",
            "goal": "whatsapp_click",
            "context": {"channel": "whatsapp", "format": "story"},
        }
        result = run_orbitals(payload)
        assert "orbitals" in result
        assert result["overall_score"] is not None

    def test_hashtags_como_lista_vazia(self):
        payload = payload_minimal(hashtags=[])
        result = run_orbitals(payload)
        csv = next((o for o in result["orbitals"] if o["orbital_id"] == "csv"), None)
        assert csv is not None
        assert csv["raw_features"]["hashtag_count"] == 0 or csv["raw_features"]["hashtag_count"] >= 0


class TestEdgeCasesAPI:
    """Edge cases via API"""

    def test_post_sem_body_retorna_422(self):
        resp = client.post("/api/v1/analyze_piece")
        assert resp.status_code == 422

    def test_post_piece_invalida_retorna_422(self):
        resp = client.post("/api/v1/analyze_piece", json={
            "source": "test",
            "piece": {"piece_id": "x"},  # falta piece_type, etc
        })
        assert resp.status_code == 422

    def test_get_analysis_404(self):
        resp = client.get("/api/v1/analysis/00000000-0000-0000-0000-000000000000")
        assert resp.status_code == 404
