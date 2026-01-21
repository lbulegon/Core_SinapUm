"""
Modelos Pydantic para API v1
"""

from typing import Optional, Dict, List, Literal
from pydantic import BaseModel, Field


class PieceAsset(BaseModel):
    """Asset da peça (imagem, vídeo, etc)"""
    asset_url: Optional[str] = Field(None, description="URL do asset")
    asset_base64: Optional[str] = Field(None, description="Asset em base64")
    mime_type: Optional[str] = Field(None, description="Tipo MIME")
    width: Optional[int] = Field(None, description="Largura")
    height: Optional[int] = Field(None, description="Altura")


class Piece(BaseModel):
    """Peça do Creative Engine"""
    piece_id: str = Field(..., description="ID único da peça")
    piece_type: Literal["image", "text", "video"] = Field(..., description="Tipo da peça")
    created_at: Optional[str] = Field(None, description="Data de criação (ISO 8601)")
    asset: Optional[PieceAsset] = Field(None, description="Asset da peça")
    text_overlay: Optional[str] = Field(None, description="Texto sobreposto")
    caption: Optional[str] = Field(None, description="Legenda/caption")
    hashtags: Optional[List[str]] = Field(default_factory=list, description="Hashtags")
    language: Optional[str] = Field("pt-BR", description="Idioma")


class Brand(BaseModel):
    """Informações da marca"""
    brand_id: Optional[str] = Field(None, description="ID da marca")
    name: Optional[str] = Field(None, description="Nome da marca")
    tone: Optional[str] = Field(None, description="Tom da marca")
    palette: Optional[List[str]] = Field(default_factory=list, description="Paleta de cores")
    category: Optional[str] = Field(None, description="Categoria")


class Objective(BaseModel):
    """Objetivo da peça"""
    primary_goal: str = Field(..., description="Objetivo principal (ex: whatsapp_click)")
    cta_expected: Optional[bool] = Field(True, description="CTA esperado")
    conversion_type: Optional[str] = Field(None, description="Tipo de conversão")


class Audience(BaseModel):
    """Audiência alvo"""
    segment: Optional[str] = Field(None, description="Segmento")
    persona: Optional[str] = Field(None, description="Persona")
    awareness_level: Optional[str] = Field(None, description="Nível de awareness")


class Distribution(BaseModel):
    """Distribuição/canal"""
    channel: str = Field(..., description="Canal (ex: whatsapp_status)")
    format: str = Field(..., description="Formato (ex: story_vertical)")
    duration_seconds: Optional[float] = Field(None, description="Duração em segundos (para vídeo)")


class Context(BaseModel):
    """Contexto adicional"""
    locale: Optional[str] = Field("pt-BR", description="Locale")
    region: Optional[str] = Field(None, description="Região")
    time_context: Optional[str] = Field(None, description="Contexto temporal")
    campaign_id: Optional[str] = Field(None, description="ID da campanha")


class Options(BaseModel):
    """Opções de processamento"""
    return_placeholders: Optional[bool] = Field(True, description="Retornar orbitais placeholder")
    explainability_level: Optional[str] = Field("full", description="Nível de explicabilidade")
    store_analysis: Optional[bool] = Field(True, description="Armazenar análise")


class AnalyzePieceRequest(BaseModel):
    """Request para análise de peça"""
    source: str = Field("vitrinezap_creative_engine", description="Origem da peça")
    source_version: Optional[str] = Field("1.0.0", description="Versão da origem")
    piece: Piece = Field(..., description="Peça a analisar")
    brand: Optional[Brand] = Field(None, description="Informações da marca")
    objective: Objective = Field(..., description="Objetivo da peça")
    audience: Optional[Audience] = Field(None, description="Audiência alvo")
    distribution: Distribution = Field(..., description="Distribuição/canal")
    context: Optional[Context] = Field(None, description="Contexto adicional")
    options: Optional[Options] = Field(None, description="Opções de processamento")


class OrbitalResultResponse(BaseModel):
    """Resposta de resultado orbital"""
    orbital_id: str
    name: str
    status: Literal["active", "placeholder", "disabled"]
    score: Optional[float] = None
    confidence: Optional[float] = None
    rationale: str
    top_features: List[str]
    raw_features: Dict
    version: str


class Insight(BaseModel):
    """Insight gerado"""
    level: Literal["low", "medium", "high"]
    title: str
    description: str
    recommendation: str


class AnalyzePieceResponse(BaseModel):
    """Resposta de análise de peça"""
    analysis_id: str = Field(..., description="ID único da análise")
    piece_id: str = Field(..., description="ID da peça analisada")
    pipeline_version: str = Field(..., description="Versão do pipeline")
    overall_score: float = Field(..., description="Score geral (0-100)")
    orbitals: List[OrbitalResultResponse] = Field(..., description="Resultados dos orbitais")
    insights: List[Insight] = Field(default_factory=list, description="Insights gerados")


class AnalysisResponse(BaseModel):
    """Resposta de consulta de análise"""
    analysis_id: str
    piece_id: str
    pipeline_version: str
    overall_score: float
    orbitals: List[OrbitalResultResponse]
    insights: List[Insight]
    created_at: str


