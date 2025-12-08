"""
Views Django para integração com Agnos
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

from .agnos_services import (
    processar_produto_com_agnos,
    validar_produto_com_agnos,
    get_workflow_manager,
    AGNOS_AVAILABLE
)

logger = logging.getLogger(__name__)


@require_http_methods(["GET", "POST"])
def analyze_with_agnos(request):
    """
    View para análise de imagens usando Agnos (orquestração de alto nível).
    Agnos coordena múltiplos CrewAI crews para workflows complexos.
    """
    if request.method == 'POST':
        if 'images' not in request.FILES:
            messages.error(request, 'Por favor, selecione pelo menos uma imagem.')
            return render(request, 'app_sinapum/analyze_agnos.html', {
                'agnos_available': AGNOS_AVAILABLE
            })
        
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
            return render(request, 'app_sinapum/analyze_agnos.html', {
                'agnos_available': AGNOS_AVAILABLE
            })
        
        # Selecionar workflow
        workflow_name = request.POST.get('workflow', 'analise_completa_produto')
        
        # Usar Agnos para processar
        try:
            result = processar_produto_com_agnos(
                image_paths,
                workflow_name=workflow_name
            )
            
            if result.get('success'):
                messages.success(
                    request,
                    f'Análise com Agnos concluída! Workflow: {workflow_name}'
                )
            else:
                messages.error(
                    request,
                    f"Erro na análise: {result.get('error', 'Erro desconhecido')}"
                )
        except Exception as e:
            logger.error(f"Erro ao processar com Agnos: {str(e)}", exc_info=True)
            messages.error(
                request,
                f"Erro ao processar com Agnos: {str(e)}"
            )
            result = {
                'success': False,
                'error': str(e)
            }
        
        context = {
            'result': result,
            'saved_images': saved_images,
            'agnos_available': AGNOS_AVAILABLE,
            'workflow_used': workflow_name
        }
        
        return render(request, 'app_sinapum/analyze_agnos.html', context)
    
    return render(request, 'app_sinapum/analyze_agnos.html', {
        'agnos_available': AGNOS_AVAILABLE
    })


@csrf_exempt
@require_http_methods(["POST"])
def api_analyze_agnos(request):
    """
    API endpoint para análise usando Agnos (retorna JSON).
    """
    try:
        data = json.loads(request.body)
        image_paths = data.get('image_paths', [])
        workflow_name = data.get('workflow', 'analise_completa_produto')
        
        if not image_paths:
            return JsonResponse({
                'success': False,
                'error': 'image_paths é obrigatório (lista de caminhos de imagens)'
            }, status=400)
        
        result = processar_produto_com_agnos(
            image_paths,
            workflow_name=workflow_name
        )
        
        return JsonResponse(result)
    
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'error': 'JSON inválido'
        }, status=400)
    except Exception as e:
        logger.error(f"Erro na API Agnos: {str(e)}", exc_info=True)
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def api_validate_agnos(request):
    """
    API endpoint para validação de dados de produto usando Agnos.
    """
    try:
        data = json.loads(request.body)
        produto_data = data.get('produto_data')
        
        if not produto_data:
            return JsonResponse({
                'success': False,
                'error': 'produto_data é obrigatório'
            }, status=400)
        
        result = validar_produto_com_agnos(produto_data)
        
        return JsonResponse(result)
    
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'error': 'JSON inválido'
        }, status=400)
    except Exception as e:
        logger.error(f"Erro na API de validação Agnos: {str(e)}", exc_info=True)
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)

