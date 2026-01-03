"""Router para Intent Classification"""
from fastapi import APIRouter, HTTPException
from app.schemas.intent import IntentRequest, IntentResponse
from app.services.intent_service import IntentService
from app.utils.logging import logger, get_request_id
from app.events.emitter import EventEmitter, EventType

router = APIRouter(prefix="/v1/intent", tags=["intent"])
intent_service = IntentService()
event_emitter = EventEmitter()


@router.post("/classify", response_model=IntentResponse)
async def classify_intent(request: IntentRequest, request_id: str = None):
    """Classifica intenção do usuário"""
    if not request_id:
        request_id = get_request_id()
    
    try:
        result = intent_service.classify(request)
        
        # Emitir evento
        event_emitter.emit(
            event_type=EventType.INTENT_DETECTED,
            request_id=request_id,
            user_id=request.user_id,
            group_id=request.group_id,
            estabelecimento_id=request.estabelecimento_id,
            payload={
                "intent": result.intent.value,
                "confidence": result.confidence,
                "urgency": result.urgency
            }
        )
        
        return result
    except Exception as e:
        logger.error(f"Erro ao classificar intent: {e}", extra={"request_id": request_id})
        raise HTTPException(status_code=500, detail=f"Erro ao classificar intent: {str(e)}")

