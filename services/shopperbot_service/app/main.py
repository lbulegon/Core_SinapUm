"""Main FastAPI application para ShopperBot Service"""
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextvars import ContextVar
from app.utils.logging import logger, get_request_id
from app.utils.config import DEBUG, PORT
from app.routers import (
    catalog, intent, recommendation, objection,
    creative, routing, handoff
)

# Context var para request_id
request_id_var: ContextVar[str] = ContextVar('request_id', default='')

app = FastAPI(
    title="ShopperBot Service",
    description="Sistema de IA Vendedora para VitrineZap",
    version="1.0.0",
    debug=DEBUG
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def add_request_id(request: Request, call_next):
    """Adiciona request_id a cada requisição"""
    request_id = request.headers.get("X-Request-ID") or get_request_id()
    request_id_var.set(request_id)
    
    response = await call_next(request)
    response.headers["X-Request-ID"] = request_id
    return response


@app.get("/health")
async def health():
    """Health check endpoint"""
    return JSONResponse({
        "status": "ok",
        "service": "shopperbot",
        "version": "1.0.0"
    })


# Incluir routers
app.include_router(catalog.router)
app.include_router(intent.router)
app.include_router(recommendation.router)
app.include_router(objection.router)
app.include_router(creative.router)
app.include_router(routing.router)
app.include_router(handoff.router)


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Handler global de exceções"""
    request_id = request_id_var.get()
    logger.error(
        f"Erro não tratado: {exc}",
        exc_info=True,
        extra={"request_id": request_id}
    )
    return JSONResponse(
        status_code=500,
        content={
            "error": "Erro interno do servidor",
            "request_id": request_id
        }
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=PORT)

