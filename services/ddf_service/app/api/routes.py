"""
Rotas da API - Endpoints do DDF
"""

from fastapi import APIRouter, HTTPException, Depends
from typing import Dict, Optional
import uuid
import time

from app.core.detect import detect_task
from app.core.delegate import delegate_task
from app.providers.provider_factory import ProviderFactory
from app.models.audit import create_audit_log
from app.mcp_tools.storage import StorageManager
from app.mcp_tools.database import DatabaseManager
from app.api.schemas import (
    DetectRequest, DetectResponse,
    DelegateRequest, DelegateResponse,
    ExecuteRequest, ExecuteResponse,
    AuditLogResponse,
    CategoriesResponse,
    ProvidersResponse
)

router = APIRouter(prefix="/ddf", tags=["DDF"])


@router.post("/detect", response_model=DetectResponse)
async def detect(request: DetectRequest):
    """
    Detecta categoria e intenção de uma tarefa
    """
    try:
        detection = detect_task(request.text, request.context)
        
        return DetectResponse(
            success=True,
            detection=detection
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/delegate", response_model=DelegateResponse)
async def delegate(request: DelegateRequest):
    """
    Delega tarefa para provider apropriado
    """
    try:
        delegation = delegate_task(request.detection, request.context)
        
        return DelegateResponse(
            success=True,
            delegation=delegation
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/execute", response_model=ExecuteResponse)
async def execute(request: ExecuteRequest):
    """
    Executa fluxo completo: Detect -> Delegate -> Execute
    """
    request_id = str(uuid.uuid4())
    start_time = time.time()
    
    try:
        text = request.text
        context = request.context
        provider_override = request.provider  # Permite sobrescrever provider
        
        if not text:
            raise HTTPException(status_code=400, detail="Campo 'text' é obrigatório")
        
        # 1. Detect
        detection = detect_task(text, context)
        
        # 2. Delegate
        delegation = delegate_task(detection, context)
        
        # 3. Escolher provider
        provider_name = provider_override or delegation.get('primary_provider')
        
        # 4. Executar
        provider_config = context.get('provider_configs', {}).get(provider_name, {})
        provider = ProviderFactory.create(provider_name, provider_config)
        
        if not provider.is_available():
            # Tentar fallback
            fallback_providers = delegation.get('fallback_providers', [])
            if fallback_providers:
                provider_name = fallback_providers[0]
                provider = ProviderFactory.create(provider_name, provider_config)
            else:
                raise HTTPException(
                    status_code=503, 
                    detail=f"Provider '{provider_name}' não está disponível"
                )
        
        result = provider.execute(text, **request.params)
        
        # 5. Salvar artefatos (se houver)
        if 'output' in result and isinstance(result['output'], dict):
            if 'image_url' in result['output']:
                # Salvar imagem via MCP storage
                storage = StorageManager()
                saved_path = await storage.save_artifact(
                    request_id, 
                    result['output']['image_url'],
                    'image'
                )
                result['output']['saved_path'] = saved_path
        
        # 6. Auditoria
        execution_time = time.time() - start_time
        audit_log = create_audit_log(
            request_id=request_id,
            category=detection.get('category'),
            provider=provider_name,
            input_text=text,
            detection=detection,
            delegation=delegation,
            result=result,
            execution_time=execution_time,
            context=context
        )
        
        # Salvar no banco via MCP database
        db = DatabaseManager()
        await db.save_audit_log(audit_log)
        
        return ExecuteResponse(
            success=True,
            request_id=request_id,
            detection=detection,
            delegation=delegation,
            result=result,
            execution_time=execution_time
        )
        
    except HTTPException:
        raise
    except Exception as e:
        execution_time = time.time() - start_time
        
        # Registrar erro na auditoria
        try:
            audit_log = create_audit_log(
                request_id=request_id,
                category=detection.get('category', 'unknown'),
                provider=provider_name if 'provider_name' in locals() else 'unknown',
                input_text=text if 'text' in locals() else '',
                detection=detection if 'detection' in locals() else {},
                delegation=delegation if 'delegation' in locals() else {},
                error=str(e),
                execution_time=execution_time,
                context=context if 'context' in locals() else {}
            )
            db = DatabaseManager()
            await db.save_audit_log(audit_log)
        except:
            pass
        
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/audit/{request_id}", response_model=AuditLogResponse)
async def get_audit(request_id: str):
    """
    Obtém log de auditoria de uma requisição
    """
    try:
        db = DatabaseManager()
        audit_log = await db.get_audit_log(request_id)
        
        if not audit_log:
            raise HTTPException(status_code=404, detail="Log não encontrado")
        
        return AuditLogResponse(
            success=True,
            audit=audit_log
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/categories", response_model=CategoriesResponse)
async def list_categories():
    """
    Lista todas as categorias disponíveis
    """
    from app.core.registry import REGISTRY
    
    categories = REGISTRY.get_all_categories()
    
    return CategoriesResponse(
        success=True,
        categories=categories,
        count=len(categories)
    )


@router.get("/providers/{category}", response_model=ProvidersResponse)
async def list_providers(category: str):
    """
    Lista providers disponíveis para uma categoria
    """
    from app.core.registry import REGISTRY
    
    providers = REGISTRY.get_providers_by_category(category)
    
    if not providers:
        raise HTTPException(
            status_code=404, 
            detail=f"Categoria '{category}' não encontrada"
        )
    
    providers_metadata = [
        REGISTRY.get_provider_metadata(provider) 
        for provider in providers
    ]
    
    return ProvidersResponse(
        success=True,
        category=category,
        providers=providers,
        providers_metadata=providers_metadata
    )

