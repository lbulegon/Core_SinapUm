"""Router para Creative Card Service"""
from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
from pathlib import Path
from app.schemas.creative import CardRequest, CardResponse
from app.services.creative_service import CreativeService
from app.storage.catalog import CatalogStorage
from app.utils.logging import logger, get_request_id
from app.utils.config import CARDS_PATH
from app.events.emitter import EventEmitter, EventType

router = APIRouter(prefix="/v1/creative", tags=["creative"])
catalog_storage = CatalogStorage()
creative_service = CreativeService(catalog_storage)
event_emitter = EventEmitter()


@router.post("/card", response_model=CardResponse)
async def generate_card(request: CardRequest, request_id: str = None):
    """Gera card do produto preservando foto original"""
    if not request_id:
        request_id = get_request_id()
    
    try:
        result = creative_service.generate_card(request)
        
        # Emitir evento
        event_emitter.emit(
            event_type=EventType.CARD_GENERATED,
            request_id=request_id,
            payload={
                "product_id": request.product_id,
                "card_url": result.card_url
            }
        )
        
        return result
    except ValueError as e:
        logger.error(f"Erro de validação ao gerar card: {e}", extra={"request_id": request_id})
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Erro ao gerar card: {e}", extra={"request_id": request_id})
        raise HTTPException(status_code=500, detail=f"Erro ao gerar card: {str(e)}")


@router.get("/card/{filename}")
async def get_card(filename: str):
    """Serve arquivo de card gerado"""
    card_path = CARDS_PATH / filename
    if not card_path.exists():
        raise HTTPException(status_code=404, detail="Card não encontrado")
    
    return FileResponse(card_path, media_type="image/png")

