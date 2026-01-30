"""
Fixtures e factories para testes do SparkScore
"""

import pytest
from typing import Dict, Optional, List


def payload_minimal(
    piece_id: str = "ce_test_001",
    text_overlay: str = "PROMOÇÃO HOJE",
    caption: str = "Chame no WhatsApp",
    piece_type: str = "image",
    primary_goal: str = "whatsapp_click",
    channel: str = "whatsapp_status",
    format_type: str = "story_vertical",
    hashtags: Optional[List[str]] = None,
    **overrides
) -> Dict:
    """
    Cria payload mínimo válido para Creative Engine.
    """
    payload = {
        "source": "vitrinezap_creative_engine",
        "piece": {
            "piece_id": piece_id,
            "piece_type": piece_type,
            "text_overlay": text_overlay,
            "caption": caption,
        },
        "objective": {"primary_goal": primary_goal},
        "distribution": {"channel": channel, "format": format_type},
    }
    if hashtags is not None:
        payload["piece"]["hashtags"] = hashtags
    payload.update(overrides)
    return payload


def payload_full(**overrides) -> Dict:
    """Payload completo com brand, audience, context, options."""
    base = payload_minimal(
        piece_id="ce_2026_01_16_000123",
        text_overlay="PROMOÇÃO SÓ HOJE",
        caption="Chame no WhatsApp e aproveite",
        hashtags=["#promoção", "#oferta", "#whatsapp"],
    )
    base["piece"]["created_at"] = "2026-01-16T14:32:10Z"
    base["piece"]["asset"] = {
        "asset_url": "https://cdn.vitrinezap.com/creatives/abc123.png",
        "mime_type": "image/png",
        "width": 1080,
        "height": 1920,
    }
    base["piece"]["language"] = "pt-BR"
    base["brand"] = {
        "brand_id": "vitrinezap",
        "name": "VitrineZap",
        "tone": "direto, amigável",
    }
    base["objective"]["cta_expected"] = True
    base["objective"]["conversion_type"] = "conversa_whatsapp"
    base["audience"] = {"segment": "varejo_local", "persona": "consumidor_proximo"}
    base["context"] = {"locale": "pt-BR", "region": "BR-RS"}
    base["options"] = {
        "return_placeholders": True,
        "explainability_level": "full",
        "store_analysis": True,
    }
    base.update(overrides)
    return base


@pytest.fixture
def minimal_payload():
    """Payload mínimo para análise."""
    return payload_minimal()


@pytest.fixture
def full_payload():
    """Payload completo para análise."""
    return payload_full()


@pytest.fixture
def payload_com_circulacao():
    """Payload otimizado para circulação: CTA, compartilhe, hashtags."""
    return payload_minimal(
        text_overlay="50% OFF - Chame no WhatsApp #oferta #promo",
        caption="Compartilhe com seus amigos",
        hashtags=["#oferta", "#promo"],
    )


@pytest.fixture
def payload_sem_cta():
    """Payload sem CTA explícito."""
    return payload_minimal(
        text_overlay="PROMOÇÃO",
        caption="Aproveite nossa oferta",
    )


@pytest.fixture
def payload_texto_longo():
    """Payload com texto excessivamente longo (obstáculo à circulação)."""
    texto = " ".join(["palavra"] * 60)
    return payload_minimal(text_overlay=texto[:200], caption=texto[200:400])


@pytest.fixture
def payload_vazio():
    """Payload com texto praticamente vazio."""
    return payload_minimal(text_overlay="", caption="")
