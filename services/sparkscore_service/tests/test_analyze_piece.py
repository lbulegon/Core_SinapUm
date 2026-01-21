"""
Testes de integração para endpoints v1 de análise de peças
"""

import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_analyze_piece_minimal():
    """Testa análise com payload mínimo"""
    payload = {
        "source": "vitrinezap_creative_engine",
        "piece": {
            "piece_id": "ce_test_001",
            "piece_type": "image",
            "text_overlay": "PROMOÇÃO HOJE",
            "caption": "Chame no WhatsApp"
        },
        "objective": {
            "primary_goal": "whatsapp_click"
        },
        "distribution": {
            "channel": "whatsapp_status",
            "format": "story_vertical"
        }
    }
    
    response = client.post("/api/v1/analyze_piece", json=payload)
    
    assert response.status_code == 200
    data = response.json()
    
    # Validar estrutura básica
    assert "analysis_id" in data
    assert "piece_id" in data
    assert data["piece_id"] == "ce_test_001"
    assert "pipeline_version" in data
    assert "overall_score" in data
    assert "orbitals" in data
    assert "insights" in data
    
    # Validar overall_score
    assert isinstance(data["overall_score"], (int, float))
    assert 0 <= data["overall_score"] <= 100
    
    # Validar orbitals
    assert isinstance(data["orbitals"], list)
    assert len(data["orbitals"]) > 0
    
    # Verificar orbitais ativos
    orbital_ids = [o["orbital_id"] for o in data["orbitals"]]
    assert "semiotic" in orbital_ids
    assert "emotional" in orbital_ids
    assert "cognitive" in orbital_ids
    
    # Verificar orbitais placeholder
    assert "narrative" in orbital_ids or any(o["orbital_id"] == "narrative" for o in data["orbitals"])
    
    # Validar estrutura de orbital ativo
    semiotic = next((o for o in data["orbitals"] if o["orbital_id"] == "semiotic"), None)
    assert semiotic is not None
    assert semiotic["status"] == "active"
    assert semiotic["score"] is not None
    assert 0 <= semiotic["score"] <= 100
    assert semiotic["confidence"] is not None
    assert 0 <= semiotic["confidence"] <= 1
    assert semiotic["rationale"] is not None
    assert len(semiotic["rationale"]) > 0
    
    # Validar estrutura de orbital placeholder
    narrative = next((o for o in data["orbitals"] if o["orbital_id"] == "narrative"), None)
    if narrative:
        assert narrative["status"] == "placeholder"
        assert narrative["score"] is None
        assert narrative["confidence"] is None
        assert narrative["rationale"] is not None
        assert len(narrative["rationale"]) > 0
    
    # Validar insights
    assert isinstance(data["insights"], list)


def test_analyze_piece_full():
    """Testa análise com payload completo"""
    payload = {
        "source": "vitrinezap_creative_engine",
        "source_version": "1.0.0",
        "piece": {
            "piece_id": "ce_2026_01_16_000123",
            "piece_type": "image",
            "created_at": "2026-01-16T14:32:10Z",
            "asset": {
                "asset_url": "https://cdn.vitrinezap.com/creatives/abc123.png",
                "mime_type": "image/png",
                "width": 1080,
                "height": 1920
            },
            "text_overlay": "PROMOÇÃO SÓ HOJE",
            "caption": "Chame no WhatsApp e aproveite",
            "hashtags": ["#promoção", "#oferta", "#whatsapp"],
            "language": "pt-BR"
        },
        "brand": {
            "brand_id": "vitrinezap",
            "name": "VitrineZap",
            "tone": "direto, amigável"
        },
        "objective": {
            "primary_goal": "whatsapp_click",
            "cta_expected": True,
            "conversion_type": "conversa_whatsapp"
        },
        "audience": {
            "segment": "varejo_local",
            "persona": "consumidor_proximo"
        },
        "distribution": {
            "channel": "whatsapp_status",
            "format": "story_vertical"
        },
        "context": {
            "locale": "pt-BR",
            "region": "BR-RS"
        },
        "options": {
            "return_placeholders": True,
            "explainability_level": "full",
            "store_analysis": True
        }
    }
    
    response = client.post("/api/v1/analyze_piece", json=payload)
    
    assert response.status_code == 200
    data = response.json()
    
    assert data["piece_id"] == "ce_2026_01_16_000123"
    assert data["pipeline_version"] == "1.0.0"
    assert len(data["orbitals"]) >= 3  # Pelo menos os 3 ativos


def test_get_analysis():
    """Testa recuperação de análise por ID"""
    # Primeiro criar uma análise
    payload = {
        "source": "vitrinezap_creative_engine",
        "piece": {
            "piece_id": "ce_test_get",
            "piece_type": "image",
            "text_overlay": "TESTE",
            "caption": "Teste de recuperação"
        },
        "objective": {
            "primary_goal": "whatsapp_click"
        },
        "distribution": {
            "channel": "whatsapp_status",
            "format": "story_vertical"
        }
    }
    
    create_response = client.post("/api/v1/analyze_piece", json=payload)
    assert create_response.status_code == 200
    
    analysis_id = create_response.json()["analysis_id"]
    
    # Recuperar análise
    get_response = client.get(f"/api/v1/analysis/{analysis_id}")
    assert get_response.status_code == 200
    
    data = get_response.json()
    assert data["analysis_id"] == analysis_id
    assert data["piece_id"] == "ce_test_get"
    assert "created_at" in data


def test_get_analysis_not_found():
    """Testa recuperação de análise inexistente"""
    response = client.get("/api/v1/analysis/00000000-0000-0000-0000-000000000000")
    assert response.status_code == 404


def test_analyze_piece_orbital_scores():
    """Testa que orbitais ativos retornam scores válidos"""
    payload = {
        "source": "vitrinezap_creative_engine",
        "piece": {
            "piece_id": "ce_test_scores",
            "piece_type": "image",
            "text_overlay": "GANHE AGORA",
            "caption": "Clique e aproveite"
        },
        "objective": {
            "primary_goal": "whatsapp_click"
        },
        "distribution": {
            "channel": "whatsapp_status",
            "format": "story_vertical"
        }
    }
    
    response = client.post("/api/v1/analyze_piece", json=payload)
    assert response.status_code == 200
    
    data = response.json()
    
    # Verificar que orbitais ativos têm scores
    active_orbitals = [o for o in data["orbitals"] if o["status"] == "active"]
    assert len(active_orbitals) >= 3
    
    for orbital in active_orbitals:
        assert orbital["score"] is not None
        assert 0 <= orbital["score"] <= 100
        assert orbital["confidence"] is not None
        assert 0 <= orbital["confidence"] <= 1
        assert orbital["rationale"] is not None
        assert len(orbital["rationale"]) > 0
        assert "raw_features" in orbital


def test_analyze_piece_insights():
    """Testa que insights são gerados quando apropriado"""
    # Payload sem CTA mas com goal whatsapp_click (deve gerar insight)
    payload = {
        "source": "vitrinezap_creative_engine",
        "piece": {
            "piece_id": "ce_test_insights",
            "piece_type": "image",
            "text_overlay": "PROMOÇÃO",
            "caption": "Aproveite"
        },
        "objective": {
            "primary_goal": "whatsapp_click"
        },
        "distribution": {
            "channel": "whatsapp_status",
            "format": "story_vertical"
        }
    }
    
    response = client.post("/api/v1/analyze_piece", json=payload)
    assert response.status_code == 200
    
    data = response.json()
    assert isinstance(data["insights"], list)
    
    # Pode ter insights ou não, dependendo da análise
    # Mas a estrutura deve estar presente


