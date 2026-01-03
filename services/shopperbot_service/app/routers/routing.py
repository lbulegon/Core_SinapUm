"""Router para Conversation Routing"""
from fastapi import APIRouter, HTTPException
from app.schemas.routing import RouteRequest, RouteResponse
from app.services.routing_service import RoutingService
from app.utils.logging import logger, get_request_id
from app.events.emitter import EventEmitter, EventType

router = APIRouter(prefix="/v1/conversation", tags=["routing"])
routing_service = RoutingService()
event_emitter = EventEmitter()


@router.post("/route", response_model=RouteResponse)
async def route_conversation(request: RouteRequest, request_id: str = None):
    """Roteia conversa (grupo → privado → humano)"""
    if not request_id:
        request_id = get_request_id()
    
    try:
        result = routing_service.route(request)
        
        # Emitir evento se for private_chat
        if result.next_step == "private_chat":
            event_emitter.emit(
                event_type=EventType.PRIVATE_CHAT_STARTED,
                request_id=request_id,
                user_id=request.user_id,
                group_id=request.group_id,
                estabelecimento_id=request.estabelecimento_id,
                payload={
                    "intent": request.intent_payload.intent.value,
                    "confidence": request.intent_payload.confidence
                }
            )
        
        return result
    except Exception as e:
        logger.error(f"Erro ao rotear conversa: {e}", extra={"request_id": request_id})
        raise HTTPException(status_code=500, detail=f"Erro ao rotear conversa: {str(e)}")

