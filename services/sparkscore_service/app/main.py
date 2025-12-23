"""
Main - Entrypoint da API FastAPI SparkScore
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.routes import router

app = FastAPI(
    title="SparkScore - Sistema de Análise Psicológica e Semiótica",
    description="Análise orbital de estímulos baseada em teoria de Peirce",
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
        "service": "SparkScore - Sistema de Análise Psicológica e Semiótica",
        "status": "online",
        "version": "1.0.0"
    }


@app.get("/health")
async def health():
    """Health check detalhado"""
    return {
        "status": "healthy",
        "service": "SparkScore"
    }

