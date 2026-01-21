"""
API v1 - Endpoints para análise de peças do Creative Engine
"""

import uuid
from datetime import datetime
from typing import Dict
from fastapi import APIRouter, HTTPException
from app.api.models import (
    AnalyzePieceRequest,
    AnalyzePieceResponse,
    AnalysisResponse
)
from app.orbitals.pipeline import run_orbitals

# Armazenamento in-memory (para MVP)
# Em produção, substituir por banco de dados
_analysis_store: Dict[str, Dict] = {}

router = APIRouter(prefix="/api/v1", tags=["API v1"])


@router.post("/analyze_piece", response_model=AnalyzePieceResponse)
async def analyze_piece(request: AnalyzePieceRequest):
    """
    Analisa uma peça do Creative Engine usando orbitais
    
    Endpoint para integração com o Creative Engine do VitrineZap.
    Analisa a peça através de múltiplos orbitais (semiótico, emocional, cognitivo, etc)
    e retorna scores, insights e recomendações.
    """
    try:
        # Converter request para dict para o pipeline
        payload = request.model_dump()
        
        # Executar pipeline orbital
        result = run_orbitals(payload)
        
        # Gerar ID único para a análise
        analysis_id = str(uuid.uuid4())
        
        # Preparar resposta
        response_data = {
            "analysis_id": analysis_id,
            "piece_id": request.piece.piece_id,
            "pipeline_version": result["pipeline_version"],
            "overall_score": result["overall_score"],
            "orbitals": result["orbitals"],
            "insights": result["insights"]
        }
        
        # Armazenar análise se solicitado
        if request.options is None or request.options.store_analysis:
            _analysis_store[analysis_id] = {
                **response_data,
                "created_at": datetime.utcnow().isoformat() + "Z"
            }
        
        return AnalyzePieceResponse(**response_data)
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao processar análise: {str(e)}"
        )


@router.get("/analysis/{analysis_id}", response_model=AnalysisResponse)
async def get_analysis(analysis_id: str):
    """
    Recupera uma análise anterior pelo ID
    
    Retorna a análise completa armazenada, incluindo todos os orbitais
    e insights gerados.
    """
    if analysis_id not in _analysis_store:
        raise HTTPException(
            status_code=404,
            detail=f"Análise '{analysis_id}' não encontrada"
        )
    
    stored = _analysis_store[analysis_id]
    
    return AnalysisResponse(**stored)


