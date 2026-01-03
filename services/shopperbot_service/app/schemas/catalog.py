"""Schemas para Catalog Index Service"""
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime


class ProductImage(BaseModel):
    url: str
    is_primary: bool = False


class ProductIndex(BaseModel):
    """Payload para indexar um produto"""
    product_id: str
    titulo: str
    descricao: Optional[str] = None
    preco: float
    imagens: List[ProductImage] = []
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


class ProductSearchResult(BaseModel):
    """Resultado de busca de produto"""
    product_id: str
    titulo: str
    descricao: Optional[str] = None
    preco: float
    imagem_principal: Optional[str] = None
    categoria: Optional[str] = None
    score: float = 0.0
    highlights: List[str] = []


class ProductSearchResponse(BaseModel):
    """Resposta de busca"""
    query: str
    total: int
    results: List[ProductSearchResult]
    estabelecimento_id: str

