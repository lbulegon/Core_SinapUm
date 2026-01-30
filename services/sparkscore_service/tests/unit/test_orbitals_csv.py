"""
Unit tests para o Orbital Circulação Simbólica Vetorial (CSV)
"""

import pytest
from app.orbitals.csv_orbital import CsvOrbital
from tests.conftest import payload_minimal


class TestCsvOrbital:
    """Testes unitários do orbital CSV"""

    @pytest.fixture
    def orbital(self):
        return CsvOrbital()

    def test_orbital_id_e_name(self, orbital):
        assert orbital.orbital_id == "csv"
        assert "Circulação Simbólica Vetorial" in orbital.name

    def test_resultado_estrutura_valida(self, orbital):
        payload = payload_minimal(
            text_overlay="Chame no WhatsApp #oferta",
            caption="Compartilhe",
        )
        result = orbital.analyze(payload)
        assert result.orbital_id == "csv"
        assert result.status == "active"
        assert result.score is not None
        assert 0 <= result.score <= 100
        assert result.confidence is not None
        assert 0 <= result.confidence <= 1
        assert result.rationale
        assert isinstance(result.raw_features, dict)
        assert isinstance(result.top_features, list)

    def test_raw_features_presentes(self, orbital):
        payload = payload_minimal(
            text_overlay="Compartilhe no WhatsApp #promo",
            caption="Chame agora",
        )
        result = orbital.analyze(payload)
        expected_keys = [
            "hashtag_count",
            "circulation_triggers_found",
            "share_invitation_detected",
            "vector_clarity",
            "channel_circulation_fit",
            "obstacle_score",
        ]
        for key in expected_keys:
            assert key in result.raw_features

    def test_hashtags_detectadas(self, orbital):
        payload = payload_minimal(
            text_overlay="Oferta #promo #oferta #vem",
            caption="",
        )
        result = orbital.analyze(payload)
        assert result.raw_features["hashtag_count"] >= 2
        assert result.raw_features["circulation_triggers_found"] >= 2

    def test_share_invitation_detectada(self, orbital):
        payload = payload_minimal(
            text_overlay="Compartilhe com amigos",
            caption="",
        )
        result = orbital.analyze(payload)
        assert result.raw_features["share_invitation_detected"] is True

    def test_vector_clarity_alta_com_cta_e_goal(self, orbital):
        payload = payload_minimal(
            text_overlay="Chame no WhatsApp e aproveite",
            caption="Clique agora",
            primary_goal="whatsapp_click",
        )
        result = orbital.analyze(payload)
        assert result.raw_features["vector_clarity"] > 0.6

    def test_channel_fit_whatsapp_story(self, orbital):
        payload = payload_minimal(
            channel="whatsapp_status",
            format_type="story_vertical",
        )
        result = orbital.analyze(payload)
        assert result.raw_features["channel_circulation_fit"] >= 0.8

    def test_obstacle_score_baixo_texto_curto(self, orbital):
        payload = payload_minimal(
            text_overlay="PROMO HOJE",
            caption="Chame",
        )
        result = orbital.analyze(payload)
        assert result.raw_features["obstacle_score"] < 0.3

    def test_obstacle_score_alto_texto_longo(self, orbital):
        texto = " ".join(["palavra"] * 55)
        payload = payload_minimal(text_overlay=texto, caption="")
        result = orbital.analyze(payload)
        assert result.raw_features["obstacle_score"] > 0.3

    def test_score_maior_com_gatilhos(self, orbital):
        payload_rico = payload_minimal(
            text_overlay="Compartilhe - Chame no WhatsApp #oferta",
            caption="Envie para amigos",
        )
        payload_pobre = payload_minimal(
            text_overlay="Oferta",
            caption="",
        )
        result_rico = orbital.analyze(payload_rico)
        result_pobre = orbital.analyze(payload_pobre)
        assert result_rico.score > result_pobre.score

    def test_payload_vazio_nao_quebra(self, orbital):
        payload = payload_minimal(text_overlay="", caption="")
        result = orbital.analyze(payload)
        assert result.status == "active"
        assert result.score is not None
        assert result.raw_features["obstacle_score"] == 0.0
