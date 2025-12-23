"""
Main - Entrypoint da API FastAPI
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.routes import router

app = FastAPI(
    title="DDF - Detect & Delegate Framework",
    description="Barramento inteligente de tarefas de IA",
    version="1.0.0"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Rotas
app.include_router(router)


@app.get("/")
async def root():
    """Health check"""
    return {
        "service": "DDF - Detect & Delegate Framework",
        "status": "online",
        "version": "1.0.0"
    }


@app.get("/health")
async def health():
    """Health check detalhado"""
    return {
        "status": "healthy",
        "service": "DDF"
    }

