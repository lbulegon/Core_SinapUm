"""Testes para Recommendation Service"""
import pytest
from app.services.recommendation_service import RecommendationService
from app.storage.catalog import CatalogStorage
from app.schemas.recommendation import RecommendationRequest, RecommendationFilter
from app.schemas.intent import IntentResponse, IntentType, ExtractedEntity


@pytest.fixture
def catalog_storage(tmp_path):
    from pathlib import Path
    storage = CatalogStorage(db_path=tmp_path / "test_catalog.db")
    return storage


@pytest.fixture
def recommendation_service(catalog_storage):
    return RecommendationService(catalog_storage)


def test_recommend_with_empty_catalog(recommendation_service):
    """Testa recomendação com catálogo vazio"""
    intent_response = IntentResponse(
        intent=IntentType.BUY_NOW,
        urgency=0.7,
        confidence=0.8,
        extracted_entities=ExtractedEntity()
    )
    
    request = RecommendationRequest(
        intent_payload=intent_response,
        filtros=RecommendationFilter(
            estabelecimento_id="est123",
            max_results=5
        )
    )
    
    result = recommendation_service.recommend(request)
    assert result.products == []
    assert result.intent == IntentType.BUY_NOW

