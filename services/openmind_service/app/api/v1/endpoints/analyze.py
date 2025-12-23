"""
Endpoint de análise de imagens
"""
from fastapi import APIRouter, UploadFile, File, HTTPException, Form, Request
from fastapi.responses import JSONResponse
from typing import Optional
import base64
import uuid
import logging
import json
from pathlib import Path
from PIL import Image
import io

from app.core.config import settings
from app.models.schemas import AnalyzeResponse
from app.core.image_analyzer import ImageAnalyzer

router = APIRouter()
logger = logging.getLogger(__name__)

# Inicializar analisador de imagens
analyzer = ImageAnalyzer()


@router.post("/analyze", response_model=AnalyzeResponse)
async def analyze_image(
    file: Optional[UploadFile] = File(None),
    image_url: Optional[str] = Form(None),
    image_base64: Optional[str] = Form(None),
    prompt: Optional[str] = Form(None)
):
    """
    Analisa uma imagem e retorna informações estruturadas em JSON
    
    Aceita:
    - Upload de arquivo (multipart/form-data)
    - URL da imagem
    - Imagem em base64
    """
    try:
        # Validar que pelo menos um método de imagem foi fornecido
        if not file and not image_url and not image_base64:
            raise HTTPException(
                status_code=400,
                detail="É necessário fornecer uma imagem (file, image_url ou image_base64)"
            )
        
        # Processar imagem
        image_data = None
        image_format = None
        
        if file:
            # Upload de arquivo
            image_data = await file.read()
            image_format = file.content_type
            filename = file.filename or "uploaded_image"
        elif image_base64:
            # Base64
            try:
                # Remover prefixo se existir (data:image/jpeg;base64,...)
                if "," in image_base64:
                    image_base64 = image_base64.split(",")[1]
                image_data = base64.b64decode(image_base64)
                image_format = "image/jpeg"  # Assumir JPEG se não especificado
                filename = "base64_image.jpg"
            except Exception as e:
                raise HTTPException(status_code=400, detail=f"Erro ao decodificar base64: {str(e)}")
        elif image_url:
            # URL - será processado pelo analyzer
            image_data = image_url
            image_format = "url"
            filename = "url_image"
        
        # Validar tamanho
        if isinstance(image_data, bytes) and len(image_data) > settings.max_image_size_bytes:
            raise HTTPException(
                status_code=400,
                detail=f"Imagem muito grande. Tamanho máximo: {settings.MAX_IMAGE_SIZE_MB}MB"
            )
        
        # Salvar imagem localmente
        if isinstance(image_data, bytes):
            # Criar diretório de uploads
            upload_dir = Path(settings.MEDIA_ROOT) / "uploads"
            upload_dir.mkdir(parents=True, exist_ok=True)
            
            # Gerar nome único
            file_extension = Path(filename).suffix or ".jpg"
            unique_filename = f"{uuid.uuid4()}{file_extension}"
            file_path = upload_dir / unique_filename
            
            # Salvar arquivo
            with open(file_path, "wb") as f:
                f.write(image_data)
            
            # Caminho relativo para retorno
            image_path = f"media/uploads/{unique_filename}"
            
            # Construir URL completa
            media_host = settings.MEDIA_HOST or f"http://localhost:{settings.OPENMIND_AI_PORT}"
            image_url_full = f"{media_host}{settings.MEDIA_URL}/uploads/{unique_filename}"
        else:
            # URL - não salva localmente
            image_path = None
            image_url_full = image_url
        
        # Analisar imagem
        logger.info(f"Analisando imagem: {filename}")
        analysis_result = await analyzer.analyze(
            image_data=image_data if isinstance(image_data, bytes) else image_url,
            prompt=prompt
        )
        
        return AnalyzeResponse(
            success=True,
            data=analysis_result,
            image_path=image_path,
            image_url=image_url_full
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao analisar imagem: {str(e)}", exc_info=True)
        return AnalyzeResponse(
            success=False,
            error=str(e),
            error_code="ANALYSIS_ERROR"
        )


@router.post("/analyze-product-image")
async def analyze_product_image(
    request: Request,
    image: Optional[UploadFile] = File(None),
    prompt: Optional[str] = Form(None),
    prompt_params: Optional[str] = Form(None)
):
    """
    Endpoint de compatibilidade para análise de imagens de produtos.
    Mantém compatibilidade com chamadas do Django/Vitrinezap.
    
    Aceita:
    - image: Arquivo de imagem único (multipart/form-data)
    - images: Lista de arquivos de imagem (multipart/form-data)
    
    Retorna formato compatível com o esperado pelo Django.
    """
    try:
        # Determinar qual arquivo usar (prioridade: image > images[0])
        file = None
        if image:
            file = image
        else:
            # Tentar obter do form-data como "images"
            form = await request.form()
            if "images" in form:
                images_field = form.getlist("images")
                if images_field and len(images_field) > 0:
                    # Se for uma lista de UploadFile
                    if isinstance(images_field[0], UploadFile):
                        file = images_field[0]
                    else:
                        # Se for string, tentar converter
                        raise HTTPException(
                            status_code=400,
                            detail="Formato de arquivo 'images' não suportado"
                        )
        
        if not file:
            raise HTTPException(
                status_code=400,
                detail="É necessário fornecer uma imagem (campo 'image' ou 'images')"
            )
        
        # Usar a mesma lógica do endpoint /analyze
        image_data = await file.read()
        filename = file.filename or "uploaded_image"
        
        # Validar tamanho
        if len(image_data) > settings.max_image_size_bytes:
            raise HTTPException(
                status_code=400,
                detail=f"Imagem muito grande. Tamanho máximo: {settings.MAX_IMAGE_SIZE_MB}MB"
            )
        
        # Salvar imagem localmente
        upload_dir = Path(settings.MEDIA_ROOT) / "uploads"
        upload_dir.mkdir(parents=True, exist_ok=True)
        
        file_extension = Path(filename).suffix or ".jpg"
        unique_filename = f"{uuid.uuid4()}{file_extension}"
        file_path = upload_dir / unique_filename
        
        # Salvar arquivo
        with open(file_path, "wb") as f:
            f.write(image_data)
        
        # Caminho relativo para retorno
        image_path = f"media/uploads/{unique_filename}"
        
        # Construir URL completa
        media_host = settings.MEDIA_HOST or f"http://localhost:{settings.OPENMIND_AI_PORT}"
        image_url_full = f"{media_host}{settings.MEDIA_URL}/uploads/{unique_filename}"
        
        # Parsear parâmetros do prompt se fornecidos
        params = {}
        if prompt_params:
            try:
                params = json.loads(prompt_params)
            except json.JSONDecodeError:
                logger.warning(f"Parâmetros do prompt inválidos, usando padrões: {prompt_params}")
        
        # Analisar imagem
        logger.info(f"Analisando imagem de produto: {filename}")
        analysis_result = await analyzer.analyze(
            image_data=image_data,
            prompt=prompt,
            params=params
        )
        
        # Retornar formato compatível com Django
        return JSONResponse({
            "success": True,
            "data": analysis_result,
            "image_path": image_path,
            "image_url": image_url_full,
            "saved_filename": unique_filename
        })
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao analisar imagem de produto: {str(e)}", exc_info=True)
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "error": str(e),
                "error_code": "ANALYSIS_ERROR"
            }
        )


@router.get("/analyze/status")
async def analyze_status():
    """Status do serviço de análise"""
    return {
        "status": "operational",
        "max_image_size_mb": settings.MAX_IMAGE_SIZE_MB,
        "allowed_formats": settings.allowed_formats_list,
        "media_root": settings.MEDIA_ROOT
    }

