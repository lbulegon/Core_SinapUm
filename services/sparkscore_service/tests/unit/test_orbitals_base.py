"""
Unit tests para orbitais (estrutura comum, base_orbital, semiotic)
"""

import pytest
from app.orbitals.base_orbital import BaseOrbital
from app.orbitals.semiotic_orbital import SemioticOrbital
from app.orbitals.csv_orbital import CsvOrbital
from app.orbitals.environmental_indiciary_orbital import EnvironmentalIndiciaryOrbital
from app.orbitals.registry import OrbitalRegistry
from tests.conftest import payload_minimal


class TestBaseOrbitalHelpers:
    """Testes dos helpers da BaseOrbital"""

    def test_extract_text_content_creative_engine(self):
        orbital = CsvOrbital()
        payload = payload_minimal(
            text_overlay="  TEXTO OVERLAY  ",
            caption="  caption  ",
        )
        text = orbital.extract_text_content(payload)
        assert "texto overlay" in text
        assert "caption" in text

    def test_extract_goal(self):
        orbital = CsvOrbital()
        payload = payload_minimal(primary_goal="whatsapp_click")
        goal = orbital.extract_goal(payload)
        assert goal == "whatsapp_click"

    def test_extract_context_distribution(self):
        orbital = CsvOrbital()
        payload = payload_minimal(
            channel="whatsapp_status",
            format_type="story_vertical",
        )
        ctx = orbital.extract_context(payload)
        assert ctx["channel"] == "whatsapp_status"
        assert ctx["format"] == "story_vertical"

    def test_clamp_score(self):
        orbital = CsvOrbital()
        assert orbital.clamp_score(150) == 100.0
        assert orbital.clamp_score(-10) == 0.0
        assert orbital.clamp_score(50) == 50.0

    def test_clamp_confidence(self):
        orbital = CsvOrbital()
        assert orbital.clamp_confidence(1.5) == 1.0
        assert orbital.clamp_confidence(-0.5) == 0.0

    def test_detect_keywords(self):
        orbital = CsvOrbital()
        text = "chame no whatsapp e compartilhe"
        keywords = ["chame", "whatsapp", "compartilhe"]
        count = orbital.detect_keywords(text, keywords)
        assert count == 3


class TestSemioticOrbital:
    """Testes básicos do orbital Semiótico"""

    @pytest.fixture
    def orbital(self):
        return SemioticOrbital()

    def test_resultado_valido(self, orbital):
        payload = payload_minimal(
            text_overlay="Chame no WhatsApp",
            caption="Clique agora",
        )
        result = orbital.analyze(payload)
        assert result.orbital_id == "semiotic"
        assert result.status == "active"
        assert result.score is not None
        assert 0 <= result.score <= 100
        assert "cta_detected" in result.raw_features

    def test_cta_detectado(self, orbital):
        payload = payload_minimal(
            text_overlay="Chame no WhatsApp e compre",
        )
        result = orbital.analyze(payload)
        assert result.raw_features["cta_detected"] is True


class TestOrbitalRegistry:
    """Testes do registry de orbitais"""

    def test_csv_registrado(self):
        registry = OrbitalRegistry()
        assert "csv" in registry._orbitals

    def test_get_orbital_csv(self):
        registry = OrbitalRegistry()
        orb = registry.get_orbital("csv")
        assert orb.orbital_id == "csv"

    def test_get_placeholder_orbitals_inclui_desabilitados(self):
        registry = OrbitalRegistry()
        placeholders = registry.get_placeholder_orbitals()
        ids = [o.orbital_id for o in placeholders]
        # environmental_indiciary: enabled false (Fase 1)
        assert "environmental_indiciary" in ids

    def test_environmental_indiciary_registrado(self):
        registry = OrbitalRegistry()
        assert "environmental_indiciary" in registry._orbitals


class TestEnvironmentalIndiciaryOrbital:
    """Orbital indiciário ambiental — entrada estruturada opcional."""

    @pytest.fixture
    def orbital(self):
        return EnvironmentalIndiciaryOrbital()

    def test_placeholder_sem_indicios(self, orbital):
        payload = payload_minimal()
        r = orbital.analyze(payload)
        assert r.orbital_id == "environmental_indiciary"
        assert r.status == "placeholder"
        assert r.score is None

    def test_inferencia_com_indicios(self, orbital):
        payload = payload_minimal(
            indicios_ambientais={
                "ruido": 0.7,
                "densidade": 0.8,
                "contaminacao_artefato": 0.9,
            }
        )
        r = orbital.analyze(payload)
        assert r.status == "active"
        assert r.score is not None
        assert 0 <= r.score <= 100
        assert r.confidence is not None
        assert r.raw_features.get("estado_ambiental")
        assert "score_pressao" in r.raw_features
        assert "score_estabilidade" in r.raw_features
        assert isinstance(r.raw_features.get("alertas"), list)

    def test_indicios_via_context(self, orbital):
        payload = payload_minimal()
        payload["context"] = {
            "indicios_ambientais": {"ritmo_operacional": 0.5, "densidade": 0.2},
        }
        r = orbital.analyze(payload)
        assert r.status == "active"
        assert r.raw_features.get("estado_ambiental") == "estavel"
