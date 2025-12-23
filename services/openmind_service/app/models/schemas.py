"""
Schemas Pydantic para validação de dados
"""
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List


class HealthResponse(BaseModel):
    """Resposta do health check"""
    status: str
    version: str
    service: str


class AnalyzeRequest(BaseModel):
    """Request para análise de imagem"""
    image_url: Optional[str] = Field(None, description="URL da imagem")
    image_base64: Optional[str] = Field(None, description="Imagem em base64")
    prompt: Optional[str] = Field(None, description="Prompt adicional para análise")


class AnalyzeResponse(BaseModel):
    """Resposta da análise de imagem"""
    success: bool
    data: Optional[Dict[str, Any]] = None
    image_path: Optional[str] = None
    image_url: Optional[str] = None
    error: Optional[str] = None
    error_code: Optional[str] = None

