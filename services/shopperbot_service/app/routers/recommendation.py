"""Router para Recommendation Service"""
from fastapi import APIRouter, HTTPException
from app.schemas.recommendation import RecommendationRequest, RecommendationResponse
from app.services.recommendation_service import RecommendationService
from app.storage.catalog import CatalogStorage
from app.utils.logging import logger, get_request_id
from app.events.emitter import EventEmitter, EventType

router = APIRouter(prefix="/v1/recommend", tags=["recommendation"])
catalog_storage = CatalogStorage()
recommendation_service = RecommendationService(catalog_storage)
event_emitter = EventEmitter()


@router.post("", response_model=RecommendationResponse)
async def recommend_products(request: RecommendationRequest, request_id: str = None):
    """Recomenda produtos baseado em intenção"""
    if not request_id:
        request_id = get_request_id()
    
    try:
        result = recommendation_service.recommend(request)
        
        # Emitir evento para cada produto recomendado
        for product in result.products:
            event_emitter.emit(
                event_type=EventType.PRODUCT_RECOMMENDED,
                request_id=request_id,
                estabelecimento_id=request.filtros.estabelecimento_id,
                payload={
                    "product_id": product.product_id,
                    "score": product.score,
                    "intent": request.intent_payload.intent.value
                }
            )
        
        return result
    except Exception as e:
        logger.error(f"Erro ao recomendar produtos: {e}", extra={"request_id": request_id})
        raise HTTPException(status_code=500, detail=f"Erro ao recomendar produtos: {str(e)}")

