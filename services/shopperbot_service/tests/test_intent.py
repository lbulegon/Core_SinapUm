"""Testes para Intent Service"""
import pytest
from app.services.intent_service import IntentService
from app.schemas.intent import IntentRequest, ContextType, IntentType


@pytest.fixture
def intent_service():
    return IntentService()


def test_classify_buy_now(intent_service):
    """Testa classificação de intent BUY_NOW"""
    request = IntentRequest(
        message="quero comprar, vou levar esse produto agora",
        contexto=ContextType.GROUP,
        user_id="user123",
        estabelecimento_id="est123"
    )
    
    result = intent_service.classify(request)
    assert result.intent == IntentType.BUY_NOW
    assert result.confidence > 0.0
    assert 0.0 <= result.urgency <= 1.0


def test_classify_price_check(intent_service):
    """Testa classificação de intent PRICE_CHECK"""
    request = IntentRequest(
        message="qual o preço desse produto?",
        contexto=ContextType.GROUP,
        user_id="user123",
        estabelecimento_id="est123"
    )
    
    result = intent_service.classify(request)
    assert result.intent == IntentType.PRICE_CHECK
    assert result.confidence > 0.0


def test_classify_compare(intent_service):
    """Testa classificação de intent COMPARE"""
    request = IntentRequest(
        message="qual a diferença entre esses dois produtos?",
        contexto=ContextType.GROUP,
        user_id="user123",
        estabelecimento_id="est123"
    )
    
    result = intent_service.classify(request)
    assert result.intent == IntentType.COMPARE
    assert result.confidence > 0.0

