"""
Contrato estável para resultado de orbital
"""

from typing import Optional, List, Dict, Literal
from pydantic import BaseModel, Field


class OrbitalResult(BaseModel):
    """
    Contrato fixo para resultado de análise orbital
    """
    orbital_id: str = Field(..., description="ID único do orbital (ex: 'semiotic', 'emotional')")
    name: str = Field(..., description="Nome legível do orbital")
    status: Literal["active", "placeholder", "disabled"] = Field(
        ..., 
        description="Status do orbital: active (implementado), placeholder (futuro), disabled (desativado)"
    )
    score: Optional[float] = Field(
        None, 
        ge=0.0, 
        le=100.0, 
        description="Score do orbital (0-100), None se placeholder"
    )
    confidence: Optional[float] = Field(
        None, 
        ge=0.0, 
        le=1.0, 
        description="Confiança do score (0-1), None se placeholder"
    )
    rationale: str = Field(
        ..., 
        description="Explicação textual do resultado, sempre preenchida"
    )
    top_features: List[str] = Field(
        default_factory=list, 
        description="Lista das features mais relevantes detectadas"
    )
    raw_features: Dict = Field(
        default_factory=dict, 
        description="Features brutas extraídas (sinais, métricas, etc)"
    )
    version: str = Field(
        ..., 
        description="Versão do orbital (ex: '1.0.0', '0.1.0' para placeholder)"
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "orbital_id": "semiotic",
                "name": "Orbital Semiótico",
                "status": "active",
                "score": 75.5,
                "confidence": 0.68,
                "rationale": "CTA detectado com boa coerência entre goal e texto",
                "top_features": ["cta_detected", "goal_coherence", "low_redundancy"],
                "raw_features": {
                    "cta_detected": True,
                    "cta_keywords_found": 2,
                    "goal_match": 0.9,
                    "redundancy_score": 0.2
                },
                "version": "1.0.0"
            }
        }

