"""Router para Handoff Service"""
from fastapi import APIRouter, HTTPException
from app.schemas.handoff import HandoffRequest, HandoffResponse
from app.services.handoff_service import HandoffService
from app.utils.logging import logger, get_request_id
from app.events.emitter import EventEmitter, EventType

router = APIRouter(prefix="/v1/handoff", tags=["handoff"])
handoff_service = HandoffService()
event_emitter = EventEmitter()


@router.post("", response_model=HandoffResponse)
async def request_handoff(request: HandoffRequest, request_id: str = None):
    """Solicita handoff para atendimento humano"""
    if not request_id:
        request_id = get_request_id()
    
    try:
        result = handoff_service.request_handoff(request)
        
        # Emitir evento
        event_emitter.emit(
            event_type=EventType.HUMAN_HANDOFF,
            request_id=request_id,
            user_id=request.user_id,
            group_id=request.group_id,
            estabelecimento_id=request.estabelecimento_id,
            payload={
                "queue_id": result.queue_id,
                "suggested_role": request.suggested_human_role,
                "urgency": request.urgency
            }
        )
        
        return result
    except Exception as e:
        logger.error(f"Erro ao solicitar handoff: {e}", extra={"request_id": request_id})
        raise HTTPException(status_code=500, detail=f"Erro ao solicitar handoff: {str(e)}")

