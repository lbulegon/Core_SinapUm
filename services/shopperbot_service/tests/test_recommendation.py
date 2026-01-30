"""Testes para Recommendation Service"""
import pytest
from unittest.mock import MagicMock
from app.services.recommendation_service import RecommendationService
from app.schemas.recommendation import RecommendationRequest, RecommendationFilter
from app.schemas.intent import IntentResponse, IntentType, ExtractedEntity


@pytest.fixture
def catalog_storage():
    """Mock do CatalogStorage (usa PostgreSQL em prod, mock em testes)"""
    storage = MagicMock()
    storage.search_products.return_value = []
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

