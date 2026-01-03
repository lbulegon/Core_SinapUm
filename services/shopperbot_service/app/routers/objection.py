"""Router para Objection Service"""
from fastapi import APIRouter, HTTPException
from app.schemas.objection import ObjectionRequest, ObjectionResponse
from app.services.objection_service import ObjectionService
from app.utils.logging import logger, get_request_id
from app.events.emitter import EventEmitter, EventType

router = APIRouter(prefix="/v1/objection", tags=["objection"])
objection_service = ObjectionService()
event_emitter = EventEmitter()


@router.post("/respond", response_model=ObjectionResponse)
async def respond_objection(request: ObjectionRequest, request_id: str = None):
    """Responde a uma objeção"""
    if not request_id:
        request_id = get_request_id()
    
    try:
        result = objection_service.respond(request)
        
        # Emitir evento
        event_emitter.emit(
            event_type=EventType.OBJECTION_HANDLED,
            request_id=request_id,
            payload={
                "objection_type": result.objection_type,
                "handoff_required": result.handoff_required,
                "product_id": request.product_id
            }
        )
        
        return result
    except Exception as e:
        logger.error(f"Erro ao responder objeção: {e}", extra={"request_id": request_id})
        raise HTTPException(status_code=500, detail=f"Erro ao responder objeção: {str(e)}")

