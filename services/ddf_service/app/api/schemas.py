"""
Schemas - Modelos Pydantic para validação de dados
"""

from pydantic import BaseModel, Field
from typing import Optional, Dict, List, Any
from datetime import datetime


class DetectRequest(BaseModel):
    """Schema para requisição de detecção"""
    text: str = Field(..., description="Texto da tarefa a ser classificada")
    context: Optional[Dict[str, Any]] = Field(default={}, description="Contexto adicional")


class DetectResponse(BaseModel):
    """Schema para resposta de detecção"""
    success: bool
    detection: Dict[str, Any]


class DelegateRequest(BaseModel):
    """Schema para requisição de delegação"""
    detection: Dict[str, Any] = Field(..., description="Resultado da detecção")
    context: Optional[Dict[str, Any]] = Field(default={}, description="Contexto adicional")


class DelegateResponse(BaseModel):
    """Schema para resposta de delegação"""
    success: bool
    delegation: Dict[str, Any]


class ExecuteRequest(BaseModel):
    """Schema para requisição de execução"""
    text: str = Field(..., description="Texto da tarefa")
    context: Optional[Dict[str, Any]] = Field(default={}, description="Contexto adicional")
    provider: Optional[str] = Field(default=None, description="Provider específico (opcional)")
    params: Optional[Dict[str, Any]] = Field(default={}, description="Parâmetros adicionais")


class ExecuteResponse(BaseModel):
    """Schema para resposta de execução"""
    success: bool
    request_id: str
    detection: Dict[str, Any]
    delegation: Dict[str, Any]
    result: Dict[str, Any]
    execution_time: float


class AuditLogResponse(BaseModel):
    """Schema para log de auditoria"""
    success: bool
    audit: Dict[str, Any]


class CategoriesResponse(BaseModel):
    """Schema para lista de categorias"""
    success: bool
    categories: List[str]
    count: int


class ProvidersResponse(BaseModel):
    """Schema para lista de providers"""
    success: bool
    category: str
    providers: List[str]
    providers_metadata: List[Dict[str, Any]]

