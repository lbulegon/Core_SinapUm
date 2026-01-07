"""Schemas para Catalog Index Service"""
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime


class ProductImage(BaseModel):
    url: str
    is_primary: bool = False


class ProductVideo(BaseModel):
    """Vídeo do produto (ETAPA 1 - Gestão de Mídia Avançada)"""
    url: str
    platform: Optional[str] = None  # 'youtube', 'instagram', 'vimeo', etc.
    thumbnail_url: Optional[str] = None


class ProductIndex(BaseModel):
    """Payload para indexar um produto"""
    product_id: str
    titulo: str
    descricao: Optional[str] = None
    preco: float
    imagens: List[ProductImage] = []
    videos: List[ProductVideo] = []  # ETAPA 1 - Gestão de Mídia Avançada
    variacoes: List[ProductVariation] = []  # ETAPA 2 - Variações e Grade
    tags: List[str] = []
    categoria: Optional[str] = None
    estabelecimento_id: str
    ativo: bool = True
    metadata: Optional[dict] = None


class ProductIndexResponse(BaseModel):
    """Resposta da indexação"""
    success: bool
    product_id: str
    indexed_at: datetime
    message: Optional[str] = None


class ProductVariation(BaseModel):
    """Variação de produto (ETAPA 2 - Variações e Grade)"""
    tipo_variacao: str  # 'tamanho', 'cor', 'material', etc.
    valor_variacao: str  # 'P', 'M', 'G', 'Vermelho', etc.
    sku: Optional[str] = None
    preco_adicional: float = 0.0
    estoque_disponivel: int = 0


class ProductSearchResult(BaseModel):
    """Resultado de busca de produto"""
    product_id: str
    titulo: str
    descricao: Optional[str] = None
    preco: float
    imagem_principal: Optional[str] = None
    videos: List[ProductVideo] = []  # ETAPA 1 - Gestão de Mídia Avançada
    variacoes: List[ProductVariation] = []  # ETAPA 2 - Variações e Grade
    categoria: Optional[str] = None
    score: float = 0.0
    highlights: List[str] = []


class ProductSearchResponse(BaseModel):
    """Resposta de busca"""
    query: str
    total: int
    results: List[ProductSearchResult]
    estabelecimento_id: str

