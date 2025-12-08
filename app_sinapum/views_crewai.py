"""
Views Django para integração com CrewAI
"""
from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.contrib import messages
import json
import logging
from pathlib import Path
from django.conf import settings
import os

from .crewai_services import (
    analisar_produto_com_crew,
    processar_produto_com_multiplos_agentes,
    CREWAI_AVAILABLE
)

logger = logging.getLogger(__name__)


@require_http_methods(["GET", "POST"])
def analyze_with_crewai(request):
    """
    View para análise de imagens usando CrewAI (orquestração de agentes).
    Similar à analyze_image, mas usando CrewAI para coordenar múltiplos agentes.
    """
    if not CREWAI_AVAILABLE:
        messages.error(
            request,
            'CrewAI não está instalado. Execute: pip install crewai'
        )
        return render(request, 'app_sinapum/analyze.html', {
            'crewai_available': False
        })
    
    if request.method == 'POST':
        if 'images' not in request.FILES:
            messages.error(request, 'Por favor, selecione pelo menos uma imagem.')
            return render(request, 'app_sinapum/analyze_crewai.html', {})
        
        uploaded_files = request.FILES.getlist('images')
        saved_images = []
        
        upload_dir = Path(settings.MEDIA_ROOT) / 'uploads'
        upload_dir.mkdir(parents=True, exist_ok=True)
        
        import uuid
        image_paths = []
        
        for image_file in uploaded_files:
            if not image_file.content_type.startswith('image/'):
                messages.warning(
                    request,
                    f'Arquivo "{image_file.name}" ignorado: não é uma imagem.'
                )
                continue
            
            file_extension = os.path.splitext(image_file.name)[1]
            unique_filename = f"{uuid.uuid4()}{file_extension}"
            file_path = upload_dir / unique_filename
            
            with open(file_path, 'wb+') as destination:
                for chunk in image_file.chunks():
                    destination.write(chunk)
            
            image_paths.append(str(file_path))
            saved_images.append({
                'filename': image_file.name,
                'saved_filename': unique_filename,
                'image_path': f"media/uploads/{unique_filename}",
                'image_url': f"{settings.MEDIA_URL}uploads/{unique_filename}"
            })
        
        if not saved_images:
            messages.error(
                request,
                'Nenhuma imagem válida foi enviada para análise.'
            )
            return render(request, 'app_sinapum/analyze_crewai.html', {})
        
        # Usar CrewAI para análise
        modo_completo = request.POST.get('modo_completo', 'true') == 'true'
        
        if len(image_paths) == 1:
            # Análise de uma imagem
            result = analisar_produto_com_crew(
                image_paths[0],
                modo_completo=modo_completo
            )
        else:
            # Análise de múltiplas imagens
            result = processar_produto_com_multiplos_agentes(
                image_paths,
                incluir_anuncio=modo_completo
            )
        
        if result.get('success'):
            messages.success(
                request,
                f'Análise com CrewAI concluída! Processadas {len(saved_images)} imagem(ns).'
            )
        else:
            messages.error(
                request,
                f"Erro na análise: {result.get('error', 'Erro desconhecido')}"
            )
        
        context = {
            'result': result,
            'saved_images': saved_images,
            'crewai_available': True,
            'modo_usado': 'completo' if modo_completo else 'rapido'
        }
        
        return render(request, 'app_sinapum/analyze_crewai.html', context)
    
    return render(request, 'app_sinapum/analyze_crewai.html', {
        'crewai_available': CREWAI_AVAILABLE
    })


@csrf_exempt
@require_http_methods(["POST"])
def api_analyze_crewai(request):
    """
    API endpoint para análise usando CrewAI (retorna JSON).
    """
    if not CREWAI_AVAILABLE:
        return JsonResponse({
            'success': False,
            'error': 'CrewAI não está instalado'
        }, status=503)
    
    try:
        data = json.loads(request.body)
        image_path = data.get('image_path')
        modo_completo = data.get('modo_completo', True)
        
        if not image_path:
            return JsonResponse({
                'success': False,
                'error': 'image_path é obrigatório'
            }, status=400)
        
        result = analisar_produto_com_crew(image_path, modo_completo=modo_completo)
        
        return JsonResponse(result)
    
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'error': 'JSON inválido'
        }, status=400)
    except Exception as e:
        logger.error(f"Erro na API CrewAI: {str(e)}", exc_info=True)
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)

