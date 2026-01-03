"""Router para Catalog Index"""
from fastapi import APIRouter, HTTPException, Query
from datetime import datetime
from typing import Optional
from app.schemas.catalog import (
    ProductIndex, ProductIndexResponse, ProductSearchResponse
)
from app.storage.catalog import CatalogStorage
from app.utils.logging import logger, get_request_id
from app.events.emitter import EventEmitter, EventType

router = APIRouter(prefix="/v1/catalog", tags=["catalog"])
catalog_storage = CatalogStorage()
event_emitter = EventEmitter()


@router.post("/index", response_model=ProductIndexResponse)
async def index_product(product: ProductIndex, request_id: str = None):
    """Indexa um produto no catálogo"""
    if not request_id:
        request_id = get_request_id()
    
    try:
        catalog_storage.index_product(product)
        logger.info(
            f"Produto indexado: {product.product_id}",
            extra={"request_id": request_id, "product_id": product.product_id}
        )
        
        return ProductIndexResponse(
            success=True,
            product_id=product.product_id,
            indexed_at=datetime.utcnow(),
            message="Produto indexado com sucesso"
        )
    except Exception as e:
        logger.error(f"Erro ao indexar produto: {e}", extra={"request_id": request_id})
        raise HTTPException(status_code=500, detail=f"Erro ao indexar produto: {str(e)}")


@router.post("/reindex/{product_id}", response_model=ProductIndexResponse)
async def reindex_product(product_id: str, product: ProductIndex, request_id: str = None):
    """Reindexa um produto existente"""
    if not request_id:
        request_id = get_request_id()
    
    if product.product_id != product_id:
        raise HTTPException(status_code=400, detail="product_id não confere")
    
    try:
        catalog_storage.index_product(product)
        return ProductIndexResponse(
            success=True,
            product_id=product_id,
            indexed_at=datetime.utcnow(),
            message="Produto reindexado com sucesso"
        )
    except Exception as e:
        logger.error(f"Erro ao reindexar produto: {e}", extra={"request_id": request_id})
        raise HTTPException(status_code=500, detail=f"Erro ao reindexar produto: {str(e)}")


@router.get("/search", response_model=ProductSearchResponse)
async def search_products(
    q: str = Query(..., min_length=1, description="Query de busca"),
    estabelecimento_id: str = Query(..., description="ID do estabelecimento"),
    categoria: Optional[str] = Query(None, description="Filtrar por categoria"),
    limit: int = Query(10, ge=1, le=50, description="Limite de resultados"),
    request_id: str = None
):
    """Busca produtos no catálogo"""
    if not request_id:
        request_id = get_request_id()
    
    try:
        results = catalog_storage.search_products(
            query=q,
            estabelecimento_id=estabelecimento_id,
            limit=limit,
            categoria=categoria
        )
        
        return ProductSearchResponse(
            query=q,
            total=len(results),
            results=results,
            estabelecimento_id=estabelecimento_id
        )
    except Exception as e:
        logger.error(f"Erro ao buscar produtos: {e}", extra={"request_id": request_id})
        raise HTTPException(status_code=500, detail=f"Erro ao buscar produtos: {str(e)}")

