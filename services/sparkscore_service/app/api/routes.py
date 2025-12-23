"""
Rotas da API - Endpoints do SparkScore
"""

from fastapi import APIRouter, HTTPException
from typing import Dict, Optional
import uuid

from app.core.sparkscore_calculator import calculate_sparkscore
from app.core.orbital_classifier import classify_orbital
from app.agents.semiotic_agent import SemioticAgent
from app.agents.psycho_agent import PsychoAgent
from app.agents.metric_agent import MetricAgent

router = APIRouter(prefix="/sparkscore", tags=["SparkScore"])


@router.post("/analyze")
async def analyze(payload: Dict):
    """
    Análise completa: SparkScore + PPA
    """
    try:
        stimulus = payload.get("stimulus", {})
        context = payload.get("context", {})
        
        if not stimulus:
            raise HTTPException(status_code=400, detail="Campo 'stimulus' é obrigatório")
        
        result = calculate_sparkscore(stimulus, context)
        
        return {
            "success": True,
            "result": result
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/classify-orbital")
async def classify_orbital_endpoint(payload: Dict):
    """
    Classifica estímulo em orbital apenas
    """
    try:
        stimulus = payload.get("stimulus", {})
        context = payload.get("context", {})
        
        if not stimulus:
            raise HTTPException(status_code=400, detail="Campo 'stimulus' é obrigatório")
        
        result = classify_orbital(stimulus, context)
        
        return {
            "success": True,
            "result": result
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/semiotic")
async def analyze_semiotic(payload: Dict):
    """
    Análise semiótica apenas
    """
    try:
        stimulus = payload.get("stimulus", {})
        context = payload.get("context", {})
        
        agent = SemioticAgent()
        result = agent.analyze(stimulus, context)
        
        return {
            "success": True,
            "result": result
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/psycho")
async def analyze_psycho(payload: Dict):
    """
    Análise psicológica apenas
    """
    try:
        stimulus = payload.get("stimulus", {})
        context = payload.get("context", {})
        
        agent = PsychoAgent()
        result = agent.analyze(stimulus, context)
        
        return {
            "success": True,
            "result": result
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/metric")
async def analyze_metric(payload: Dict):
    """
    Análise métrica apenas
    """
    try:
        stimulus = payload.get("stimulus", {})
        context = payload.get("context", {})
        
        agent = MetricAgent()
        result = agent.analyze(stimulus, context)
        
        return {
            "success": True,
            "result": result
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/orbitals")
async def list_orbitals():
    """
    Lista todos os orbitais disponíveis
    """
    import yaml
    from pathlib import Path
    
    config_path = Path(__file__).parent.parent.parent / 'config' / 'orbitals.yaml'
    with open(config_path, 'r', encoding='utf-8') as f:
        orbitals_config = yaml.safe_load(f)
    
    return {
        "success": True,
        "orbitals": orbitals_config.get('orbitals', [])
    }


@router.get("/health")
async def health():
    """Health check"""
    return {
        "status": "healthy",
        "service": "SparkScore"
    }

