from django.shortcuts import render, redirect
from django.contrib import messages
from django.views.decorators.http import require_http_methods, require_POST
from django.conf import settings
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .services import analyze_image_with_openmind, analyze_multiple_images
from .models import ProdutoJSON
import json
import os
import tempfile
import threading
import uuid
import logging
from pathlib import Path
from typing import Any, Dict, List

logger = logging.getLogger(__name__)

def home(request):
    """View para a página inicial com menu."""
    context = {
        'grafana_url': 'http://69.169.102.84:3000/login',
        'chatwoot_url': 'http://69.169.102.84:3001',
    }
    return render(request, 'app_sinapum/home.html', context)


@require_http_methods(["GET", "POST"])
def analyze_image(request):
    """View para análise de imagens com OpenMind AI. Suporta múltiplas imagens."""
    if request.method == 'POST':
        # Verificar se é uma requisição AJAX para adicionar imagens
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return handle_add_images_ajax(request)
        
        # Verificar se é uma requisição para reanalisar
        if request.POST.get('action') == 'reanalyze':
            return handle_reanalyze(request)
        
        # Verificar se há imagens (suporta múltiplas)
        if 'images' in request.FILES:
            image_files = request.FILES.getlist('images')
        elif 'image' in request.FILES:
            # Fallback para compatibilidade com upload único
            image_files = [request.FILES['image']]
        else:
            messages.error(request, 'Por favor, selecione pelo menos uma imagem.')
            return render(request, 'app_sinapum/analyze.html', {})
        
        if not image_files:
            messages.error(request, 'Por favor, selecione pelo menos uma imagem.')
            return render(request, 'app_sinapum/analyze.html', {})
        
        # Validar tipos de arquivo
        for image_file in image_files:
            if not image_file.content_type.startswith('image/'):
                messages.error(request, f'O arquivo "{image_file.name}" deve ser uma imagem.')
                return render(request, 'app_sinapum/analyze.html', {})
        
        # Salvar todas as imagens no servidor
        upload_dir = Path(settings.MEDIA_ROOT) / 'uploads'
        upload_dir.mkdir(parents=True, exist_ok=True)
        
        import uuid
        saved_images = []  # Lista de imagens salvas com seus caminhos
        
        for image_file in image_files:
            file_extension = os.path.splitext(image_file.name)[1]
            unique_filename = f"{uuid.uuid4()}{file_extension}"
            file_path = upload_dir / unique_filename
            image_path = f"media/uploads/{unique_filename}"
            image_url = f"{settings.MEDIA_URL}uploads/{unique_filename}"
            
            # Salvar arquivo
            with open(file_path, 'wb+') as destination:
                for chunk in image_file.chunks():
                    destination.write(chunk)
            
            saved_images.append({
                'file': image_file,
                'filename': image_file.name,
                'saved_filename': unique_filename,
                'image_path': image_path,
                'image_url': image_url
            })
        
        # Analisar imagens
        if len(saved_images) == 1:
            # Uma única imagem - usar método simples
            image_file = saved_images[0]['file']
            image_file.seek(0)
            image_path = saved_images[0]['image_path']
            image_url = saved_images[0]['image_url']
            result = analyze_image_with_openmind(image_file, image_path=image_path, image_url=image_url)
            
            produto_data = result.get('data', {})
            
            # A função analyze_image_with_openmind já retorna o JSON transformado no formato modelo.json
            # com prompt_info incluído no cadastro_meta. Não precisamos transformar novamente.
            # Apenas garantir que o formato está correto
            if produto_data and result.get('success'):
                # Se ainda não estiver no formato modelo.json (caso raro), transformar
                # Mas isso não deve acontecer, pois analyze_image_with_openmind já faz a transformação
                if 'produto' not in produto_data or 'produto_generico_catalogo' not in produto_data:
                    from .utils import transform_evora_to_modelo_json
                    # Tentar extrair prompt_info do resultado se disponível
                    prompt_info = None
                    if 'prompt_info' in result:
                        prompt_info = result['prompt_info']
                    elif produto_data.get('cadastro_meta', {}).get('prompt_usado'):
                        # Se já tem prompt_usado, não precisa transformar novamente
                        pass
                    else:
                        # Fallback: transformar sem prompt_info (não ideal, mas necessário)
                        produto_data = transform_evora_to_modelo_json(
                            produto_data,
                            image_filename=image_file.name,
                            image_path=image_path,
                            prompt_info=prompt_info
                        )
                
                if 'produto' in produto_data:
                    if 'imagens' not in produto_data['produto']:
                        produto_data['produto']['imagens'] = []
                    if image_path not in produto_data['produto']['imagens']:
                        produto_data['produto']['imagens'].insert(0, image_path)
                    if not produto_data['produto']['imagens']:
                        produto_data['produto']['imagens'] = [image_path]
            
            # Preparar imagens para JSON (sem objetos file)
            saved_images_json = [{
                'filename': img['filename'],
                'saved_filename': img['saved_filename'],
                'image_path': img['image_path'],
                'image_url': img['image_url']
            } for img in saved_images]
            
            context = {
                'result': result,
                'image_name': saved_images[0]['filename'],
                'image_url': saved_images[0]['image_url'],
                'saved_filename': saved_images[0]['saved_filename'],
                'image_path': image_path,
                'formatted_data': json.dumps(produto_data, indent=2, ensure_ascii=False) if produto_data else None,
                'produto_json': json.dumps(produto_data) if produto_data else None,
                'multiple_images': False,
                'saved_images_json': json.dumps(saved_images_json)
            }
        else:
            # Múltiplas imagens - usar análise comparativa
            image_files_list = [img['file'] for img in saved_images]
            result = analyze_multiple_images(image_files_list)
            
            # Adicionar caminhos das imagens salvas
            if result.get('mesmo_produto') and result.get('produto_consolidado'):
                produto_data = result['produto_consolidado']
                # Adicionar todos os caminhos das imagens
                if 'produto' in produto_data:
                    if 'imagens' not in produto_data['produto']:
                        produto_data['produto']['imagens'] = []
                    # Adicionar caminhos de todas as imagens salvas
                    for img_info in saved_images:
                        if img_info['image_path'] not in produto_data['produto']['imagens']:
                            produto_data['produto']['imagens'].append(img_info['image_path'])
            else:
                # Produtos diferentes - usar primeiro produto como base
                produto_data = result.get('produtos_diferentes', [{}])[0].get('produto_data', {}) if result.get('produtos_diferentes') else {}
            
            # Preparar imagens para JSON (sem objetos file)
            saved_images_for_template = [{
                'filename': img['filename'],
                'saved_filename': img['saved_filename'],
                'image_path': img['image_path'],
                'image_url': img['image_url']
            } for img in saved_images]
            
            context = {
                'result': result,
                'saved_images': saved_images_for_template,  # Sem objetos file para o template
                'formatted_data': json.dumps(produto_data, indent=2, ensure_ascii=False) if produto_data else None,
                'produto_json': json.dumps(produto_data) if produto_data else None,
                'multiple_images': True,
                'mesmo_produto': result.get('mesmo_produto', False),
                'consistencia': result.get('consistencia', {}),
                'aviso': result.get('aviso'),
                'saved_images_json': json.dumps(saved_images_for_template)
            }
        
        if result.get('success'):
            if len(saved_images) > 1:
                if result.get('mesmo_produto'):
                    messages.success(request, f'{len(saved_images)} imagens analisadas. Todas são do mesmo produto!')
                else:
                    messages.warning(request, f'{len(saved_images)} imagens analisadas. ATENÇÃO: As imagens parecem ser de produtos diferentes!')
            else:
                messages.success(request, 'Imagem analisada e salva com sucesso!')
        else:
            messages.error(request, f"Erro na análise: {result.get('error', 'Erro desconhecido')}")
        
        return render(request, 'app_sinapum/analyze.html', context)
    
    # GET request - mostrar formulário
    return render(request, 'app_sinapum/analyze.html', {})


def handle_add_images_ajax(request):
    """Manipula requisição AJAX para adicionar mais imagens."""
    if 'images' not in request.FILES:
        return JsonResponse({'success': False, 'error': 'Nenhuma imagem enviada'}, status=400)
    
    image_files = request.FILES.getlist('images')
    upload_dir = Path(settings.MEDIA_ROOT) / 'uploads'
    upload_dir.mkdir(parents=True, exist_ok=True)
    
    import uuid
    new_images = []
    
    for image_file in image_files:
        if not image_file.content_type.startswith('image/'):
            continue
        
        file_extension = os.path.splitext(image_file.name)[1]
        unique_filename = f"{uuid.uuid4()}{file_extension}"
        file_path = upload_dir / unique_filename
        image_path = f"media/uploads/{unique_filename}"
        image_url = f"{settings.MEDIA_URL}uploads/{unique_filename}"
        
        # Salvar arquivo
        with open(file_path, 'wb+') as destination:
            for chunk in image_file.chunks():
                destination.write(chunk)
        
        new_images.append({
            'filename': image_file.name,
            'saved_filename': unique_filename,
            'image_path': image_path,
            'image_url': image_url
        })
    
    return JsonResponse({
        'success': True,
        'new_images': new_images,
        'message': f'{len(new_images)} imagem(ns) adicionada(s) com sucesso!'
    })


def handle_reanalyze(request):
    """Manipula requisição para reanalisar imagens."""
    # Obter lista de caminhos de imagens da requisição
    image_paths = request.POST.getlist('image_paths[]')
    
    if not image_paths:
        messages.error(request, 'Nenhuma imagem para reanalisar.')
        return render(request, 'app_sinapum/analyze.html', {})
    
    # Carregar arquivos das imagens
    upload_dir = Path(settings.MEDIA_ROOT) / 'uploads'
    saved_images = []
    image_files_list = []
    
    for image_path in image_paths:
        # Extrair nome do arquivo do caminho
        filename = os.path.basename(image_path)
        file_path = upload_dir / filename
        
        if file_path.exists():
            # Recriar objeto file-like para análise
            from django.core.files.uploadedfile import InMemoryUploadedFile
            from io import BytesIO
            
            with open(file_path, 'rb') as f:
                file_content = BytesIO(f.read())
                image_file = InMemoryUploadedFile(
                    file_content,
                    None,
                    filename,
                    'image/jpeg',
                    len(file_content.getvalue()),
                    None
                )
                
                saved_images.append({
                    'filename': filename,
                    'saved_filename': filename,
                    'image_path': image_path,
                    'image_url': f"{settings.MEDIA_URL}uploads/{filename}"
                })
                image_files_list.append(image_file)
    
    if not image_files_list:
        messages.error(request, 'Erro ao carregar imagens para reanálise.')
        return render(request, 'app_sinapum/analyze.html', {})
    
    # Reanalisar todas as imagens
    if len(image_files_list) == 1:
        image_file = image_files_list[0]
        image_file.seek(0)
        image_path = saved_images[0]['image_path']
        image_url = saved_images[0]['image_url']
        result = analyze_image_with_openmind(image_file, image_path=image_path, image_url=image_url)
        
        produto_data = result.get('data', {})
        
        from .utils import transform_evora_to_modelo_json
        if produto_data and result.get('success'):
            if 'produto' not in produto_data or 'produto_generico_catalogo' not in produto_data:
                produto_data = transform_evora_to_modelo_json(
                    produto_data,
                    image_filename=saved_images[0]['filename'],
                    image_path=image_path
                )
            
            if 'produto' in produto_data:
                if 'imagens' not in produto_data['produto']:
                    produto_data['produto']['imagens'] = []
                if image_path not in produto_data['produto']['imagens']:
                    produto_data['produto']['imagens'].insert(0, image_path)
                if not produto_data['produto']['imagens']:
                    produto_data['produto']['imagens'] = [image_path]
        
        # Preparar imagens para JSON (já não contém objetos file)
        saved_images_for_template = saved_images
        
        context = {
            'result': result,
            'image_name': saved_images[0]['filename'],
            'image_url': saved_images[0]['image_url'],
            'saved_filename': saved_images[0]['saved_filename'],
            'image_path': image_path,
            'formatted_data': json.dumps(produto_data, indent=2, ensure_ascii=False) if produto_data else None,
            'produto_json': json.dumps(produto_data) if produto_data else None,
            'multiple_images': False,
            'saved_images_json': json.dumps(saved_images_for_template)
        }
    else:
        # Múltiplas imagens
        result = analyze_multiple_images(image_files_list)
        
        if result.get('mesmo_produto') and result.get('produto_consolidado'):
            produto_data = result['produto_consolidado']
            if 'produto' in produto_data:
                if 'imagens' not in produto_data['produto']:
                    produto_data['produto']['imagens'] = []
                for img_info in saved_images:
                    if img_info['image_path'] not in produto_data['produto']['imagens']:
                        produto_data['produto']['imagens'].append(img_info['image_path'])
        else:
            produto_data = result.get('produtos_diferentes', [{}])[0].get('produto_data', {}) if result.get('produtos_diferentes') else {}
        
        # Preparar imagens para JSON (já não contém objetos file)
        saved_images_for_template = saved_images
        
        context = {
            'result': result,
            'saved_images': saved_images_for_template,  # Sem objetos file para o template
            'formatted_data': json.dumps(produto_data, indent=2, ensure_ascii=False) if produto_data else None,
            'produto_json': json.dumps(produto_data) if produto_data else None,
            'multiple_images': True,
            'mesmo_produto': result.get('mesmo_produto', False),
            'consistencia': result.get('consistencia', {}),
            'aviso': result.get('aviso'),
            'saved_images_json': json.dumps(saved_images_for_template)
        }
    
    messages.success(request, f'Reanálise concluída para {len(saved_images)} imagem(ns)!')
    return render(request, 'app_sinapum/analyze.html', context)


@require_http_methods(["POST"])
def save_product_json(request):
    """View para salvar produto no banco de dados em formato JSON"""
    try:
        data = json.loads(request.body)
        produto_json = data.get('produto_json')
        
        if not produto_json:
            return JsonResponse({
                'success': False,
                'error': 'Dados do produto não fornecidos'
            }, status=400)
        
        # Extrair informações básicas para indexação
        produto = produto_json.get('produto', {})
        nome_produto = produto.get('nome', 'Produto sem nome')
        marca = produto.get('marca')
        categoria = produto.get('categoria')
        codigo_barras = produto.get('codigo_barras')
        
        # Obter caminho da imagem (primeira imagem do array)
        imagem_original = None
        if produto.get('imagens') and len(produto.get('imagens', [])) > 0:
            imagem_original = produto['imagens'][0]  # Usar primeira imagem do array (caminho completo)
        elif produto_json.get('cadastro_meta', {}).get('fonte'):
            # Fallback: tentar extrair do campo fonte se não houver no array
            imagem_original = produto_json.get('cadastro_meta', {}).get('fonte', '').split(':')[-1].strip()
        
        # Verificar se produto já existe pelo código de barras
        if codigo_barras:
            produto_existente = ProdutoJSON.objects.filter(codigo_barras=codigo_barras).first()
            if produto_existente:
                # Atualizar produto existente
                produto_existente.dados_json = produto_json
                produto_existente.nome_produto = nome_produto
                produto_existente.marca = marca
                produto_existente.categoria = categoria
                produto_existente.imagem_original = imagem_original
                produto_existente.save()
                return JsonResponse({
                    'success': True,
                    'message': 'Produto atualizado com sucesso!',
                    'action': 'updated'
                })
        
        # Criar novo produto
        ProdutoJSON.objects.create(
            dados_json=produto_json,
            nome_produto=nome_produto,
            marca=marca,
            categoria=categoria,
            codigo_barras=codigo_barras,
            imagem_original=imagem_original
        )
        
        return JsonResponse({
            'success': True,
            'message': 'Produto salvo com sucesso!',
            'action': 'created'
        })
        
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'error': 'Formato JSON inválido'
        }, status=400)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def api_analyze_product_image(request):
    """
    API endpoint REST para análise de imagem de produto.
    Salva a imagem no servidor SinapUm e retorna a URL completa.
    
    Endpoint: POST /api/v1/analyze-product-image
    Content-Type: multipart/form-data
    Body: image (arquivo de imagem)
    
    Response:
    {
        "success": true,
        "data": { ... dados do produto ... },
        "image_url": "http://69.169.102.84:5000/media/uploads/uuid.jpg",
        "image_path": "media/uploads/uuid.jpg",
        "saved_filename": "uuid.jpg"
    }
    """
    try:
        # Verificar se há imagem na requisição
        if 'image' not in request.FILES and 'images' not in request.FILES:
            return JsonResponse({
                'success': False,
                'error': 'Nenhuma imagem enviada. Use o campo "image" ou "images" no form-data.',
                'error_code': 'NO_IMAGE'
            }, status=400)
        
        # Pegar a primeira imagem (suporta tanto 'image' quanto 'images')
        if 'image' in request.FILES:
            image_file = request.FILES['image']
        else:
            image_files = request.FILES.getlist('images')
            if not image_files:
                return JsonResponse({
                    'success': False,
                    'error': 'Nenhuma imagem válida enviada.',
                    'error_code': 'NO_IMAGE'
                }, status=400)
            image_file = image_files[0]  # Usar primeira imagem para API
        
        # Validar tipo de arquivo
        if not image_file.content_type.startswith('image/'):
            return JsonResponse({
                'success': False,
                'error': f'O arquivo "{image_file.name}" deve ser uma imagem.',
                'error_code': 'INVALID_FILE_TYPE'
            }, status=400)
        
        # Salvar imagem no servidor SinapUm
        upload_dir = Path(settings.MEDIA_ROOT) / 'uploads'
        upload_dir.mkdir(parents=True, exist_ok=True)
        
        file_extension = os.path.splitext(image_file.name)[1]
        unique_filename = f"{uuid.uuid4()}{file_extension}"
        file_path = upload_dir / unique_filename
        
        # Salvar arquivo
        with open(file_path, 'wb+') as destination:
            for chunk in image_file.chunks():
                destination.write(chunk)
        
        # Gerar URLs da imagem
        # Caminho relativo (usado no JSON)
        image_path = f"media/uploads/{unique_filename}"
        
        # URL completa para acesso público
        # Usar ALLOWED_HOSTS ou request.get_host() para URL dinâmica
        host = request.get_host()
        scheme = 'https' if request.is_secure() else 'http'
        # Garantir que MEDIA_URL não tenha barra dupla
        media_url = settings.MEDIA_URL.rstrip('/')
        if not media_url.startswith('/'):
            media_url = '/' + media_url
        image_url = f"{scheme}://{host}{media_url}uploads/{unique_filename}"
        
        logger.info(f"Imagem salva: {image_path} (URL: {image_url})")
        
        # Resetar ponteiro do arquivo para análise
        image_file.seek(0)
        
        # Analisar imagem com OpenMind AI (passar image_path e image_url)
        result = analyze_image_with_openmind(image_file, image_path=image_path, image_url=image_url)
        
        # Adicionar informações da imagem salva à resposta
        if result.get('success'):
            # Adicionar image_url e image_path à resposta
            result['image_url'] = image_url
            result['image_path'] = image_path
            result['saved_filename'] = unique_filename
            
            # Se houver dados do produto, adicionar o caminho da imagem
            if result.get('data'):
                produto_data = result['data']
                
                # Se já está no formato modelo.json
                if isinstance(produto_data, dict) and 'produto' in produto_data:
                    if 'imagens' not in produto_data['produto']:
                        produto_data['produto']['imagens'] = []
                    if image_path not in produto_data['produto']['imagens']:
                        produto_data['produto']['imagens'].insert(0, image_path)
                    
                    # Atualizar fonte no cadastro_meta
                    if 'cadastro_meta' in produto_data:
                        produto_data['cadastro_meta']['fonte'] = f"Análise automática de imagem: {image_path}"
                else:
                    # Formato ÉVORA - adicionar image_path aos dados
                    if 'imagens' not in produto_data:
                        produto_data['imagens'] = []
                    if image_path not in produto_data['imagens']:
                        produto_data['imagens'].insert(0, image_path)
        else:
            # Mesmo se houver erro, retornar URL da imagem salva
            result['image_url'] = image_url
            result['image_path'] = image_path
            result['saved_filename'] = unique_filename
        
        return JsonResponse(result, status=200 if result.get('success') else 500)
        
    except Exception as e:
        logger.error(f"Erro na API de análise de imagem: {str(e)}", exc_info=True)
        return JsonResponse({
            'success': False,
            'error': str(e),
            'error_code': 'INTERNAL_ERROR'
        }, status=500)


@require_http_methods(["GET", "POST"])
def rag_gastronomico(request):
    """Upload de PDF para o vectorstore + consulta RAG (integrado ao Core)."""
    from core.services.ingestion.pdf_ingestor import ID_PREFIX, ingest_pdf_path
    from core.services.vectorstore_client import vectorstore_search

    context = {
        "rag_results": None,
        "query": "",
        "id_prefix_default": ID_PREFIX,
    }

    if request.method == "POST":
        action = (request.POST.get("action") or "upload").strip()
        if action == "search":
            q = (request.POST.get("query") or "").strip()
            context["query"] = q
            if not q:
                messages.error(request, "Informe uma pergunta ou termo para buscar no RAG.")
            else:
                k = int(request.POST.get("k") or 8)
                results = vectorstore_search(q, k=max(1, min(20, k)), include_text=True)
                prefix = (request.POST.get("id_prefix") or ID_PREFIX).strip()
                if prefix:
                    results = [
                        r for r in results if str((r or {}).get("id", "")).startswith(prefix)
                    ]
                context["rag_results"] = results
                if not results:
                    messages.warning(request, "Nenhum resultado encontrado (verifique o vectorstore e o prefixo).")
        else:
            pdf = request.FILES.get("pdf")
            if not pdf:
                messages.error(request, "Selecione um arquivo PDF.")
            elif not pdf.name.lower().endswith(".pdf"):
                messages.error(request, "Apenas arquivos PDF são aceitos.")
            else:
                tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
                try:
                    for chunk in pdf.chunks():
                        tmp.write(chunk)
                    tmp.close()
                    res = ingest_pdf_path(tmp.name, original_name=pdf.name)
                    if res.get("ok"):
                        messages.success(
                            request,
                            "PDF processado: %(chunks)s chunks enviados ao vectorstore "
                            "(%(pages)s páginas com texto). IDs: %(prefix)s:*"
                            % {
                                "chunks": res.get("chunks_ingested", 0),
                                "pages": res.get("pages", 0),
                                "prefix": ID_PREFIX,
                            },
                        )
                    else:
                        messages.error(
                            request,
                            res.get("error") or "Falha na ingestão. Verifique o serviço vectorstore (VECTORSTORE_URL).",
                        )
                finally:
                    try:
                        os.unlink(tmp.name)
                    except OSError:
                        pass

    return render(request, "app_sinapum/rag_gastronomico.html", context)


def _rag_gastro_run_job(job_id: str, path: str, original_name: str) -> None:
    from django.core.cache import cache
    from django.db import connection

    key = f"rag_gastro_job:{job_id}"
    try:
        connection.close()
    except Exception:
        pass

    def progress_cb(phase: str, pct: int, detail=None):
        cache.set(
            key,
            {
                "job_id": job_id,
                "phase": phase,
                "step": phase,
                "pct": max(0, min(100, int(pct))),
                "detail": (detail or "")[:500],
                "done": phase == "error",
                "error": detail if phase == "error" else None,
                "result": None,
            },
            3600,
        )

    try:
        from core.services.ingestion.pdf_ingestor import ID_PREFIX, ingest_pdf_path

        res = ingest_pdf_path(
            path,
            original_name=original_name,
            progress_callback=progress_cb,
        )
        if res.get("ok"):
            cache.set(
                key,
                {
                    "job_id": job_id,
                    "phase": "done",
                    "step": "done",
                    "pct": 100,
                    "detail": "Ingestão concluída",
                    "done": True,
                    "error": None,
                    "result": {
                        "chunks_ingested": res.get("chunks_ingested"),
                        "chunks_total": res.get("chunks_total"),
                        "pages": res.get("pages"),
                        "errors": res.get("errors") or [],
                        "id_prefix": ID_PREFIX,
                    },
                },
                3600,
            )
        else:
            err = res.get("error") or "Falha na ingestão"
            cache.set(
                key,
                {
                    "job_id": job_id,
                    "phase": "error",
                    "step": "error",
                    "pct": 0,
                    "detail": err,
                    "done": True,
                    "error": err,
                    "result": None,
                },
                3600,
            )
    except Exception as e:
        logger.exception("rag_gastro_run_job")
        cache.set(
            key,
            {
                "job_id": job_id,
                "phase": "error",
                "step": "error",
                "pct": 0,
                "detail": str(e),
                "done": True,
                "error": str(e),
                "result": None,
            },
            3600,
        )
    finally:
        try:
            os.unlink(path)
        except OSError:
            pass


@require_POST
def rag_gastronomico_ingest_start(request):
    """Inicia ingestão assíncrona (PDF) — devolve job_id para polling de estado."""
    from django.core.cache import cache

    pdf = request.FILES.get("pdf")
    if not pdf:
        return JsonResponse({"ok": False, "error": "Campo pdf obrigatório"}, status=400)
    if not pdf.name.lower().endswith(".pdf"):
        return JsonResponse({"ok": False, "error": "Apenas arquivos .pdf"}, status=400)

    max_mb = int(os.environ.get("RAG_GASTR_PDF_MAX_MB", "40") or 40)
    max_bytes = max(1, max_mb) * 1024 * 1024
    size = getattr(pdf, "size", None) or 0
    if size and size > max_bytes:
        return JsonResponse(
            {"ok": False, "error": f"PDF acima do limite ({max_mb} MB)"},
            status=400,
        )

    job_id = str(uuid.uuid4())
    key = f"rag_gastro_job:{job_id}"
    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
    try:
        for chunk in pdf.chunks():
            tmp.write(chunk)
        tmp.close()
        pdf_path = tmp.name
    except Exception as e:
        logger.exception("rag_gastronomico_ingest_start")
        try:
            os.unlink(tmp.name)
        except OSError:
            pass
        return JsonResponse({"ok": False, "error": str(e)}, status=500)

    cache.set(
        key,
        {
            "job_id": job_id,
            "phase": "upload",
            "step": "upload",
            "pct": 10,
            "detail": "Ficheiro recebido no servidor",
            "done": False,
            "error": None,
            "result": None,
        },
        3600,
    )

    threading.Thread(
        target=_rag_gastro_run_job,
        args=(job_id, pdf_path, pdf.name),
        daemon=True,
    ).start()

    return JsonResponse({"ok": True, "job_id": job_id})


def rag_gastronomico_ingest_status(request, job_id):
    """Estado do job (barra de progresso / resultado)."""
    from django.core.cache import cache

    try:
        uuid.UUID(str(job_id))
    except (ValueError, TypeError):
        return JsonResponse({"ok": False, "error": "job_id inválido"}, status=400)

    key = f"rag_gastro_job:{job_id}"
    data = cache.get(key)
    if not data:
        return JsonResponse({"ok": False, "error": "Job expirado ou desconhecido"}, status=404)

    return JsonResponse({"ok": True, **data})


def _rag_gastro_decision_preview(*, filename: str, chunk_count: int, pages: int) -> Dict[str, Any]:
    """DecisionEngine (estratégia) sobre a intenção de indexar conhecimento — auditoria / produto."""
    try:
        from core.services.cognitive_core.context.cognitive_context import CognitiveContext
        from core.services.cognitive_core.mediation.decision_engine import DecisionEngine
        from core.services.cognitive_core.perception.adapters import perception_from_mcp_dict
        from core.services.cognitive_core.reality.builder import RealityStateBuilder

        raw = {
            "text": "rag_gastro_preview",
            "rag_gastro_preview": True,
            "source_file": filename,
            "chunk_count": chunk_count,
            "pages": pages,
        }
        perception = perception_from_mcp_dict(raw, source="rag_gastronomico", trace_id=None)
        ctx = CognitiveContext.from_perception(
            perception,
            extra={"rag_namespaces": ["gastronomia", "global"]},
        )
        builder = RealityStateBuilder(default_rag_k=4, default_namespaces=["global", "gastronomia"])
        reality = builder.build(perception, ctx)
        proposal = {
            "proposal_id": "rag_gastro_ingest_preview",
            "tipo": "expansao",
            "titulo": f"Indexar conhecimento gastronómico ({filename})",
            "descricao": f"Pré-visualização: {chunk_count} chunks, {pages} página(s) com texto.",
            "impacto_estimado": min(0.85, 0.35 + min(chunk_count, 200) * 0.002),
            "risco": "low",
            "prioridade": "normal",
            "parametros": {"acao": "rag_ingest", "chunk_count": chunk_count, "pages": pages},
        }
        engine = DecisionEngine()
        out = engine.decide_strategic_support(
            perception=perception,
            reality=reality,
            ctx=ctx,
            strategy_proposal=proposal,
        )
        d = out.to_dict()
        return {
            "ok": True,
            "confidence": d.get("confidence"),
            "risk_level": d.get("risk_level"),
            "reasoning": (d.get("reasoning") or "")[:1200],
            "expected_outcome": (d.get("expected_outcome") or "")[:500],
            "cognitive_version": getattr(out, "cognitive_version", None) or d.get("cognitive_version"),
            "action": d.get("action"),
            "decision_score": d.get("decision_score"),
        }
    except Exception as e:
        logger.exception("_rag_gastro_decision_preview")
        return {"ok": False, "error": str(e)}


@require_POST
def rag_gastronomico_preview(request):
    """Extrai chunks + classificação, grava preview em disco, devolve snippets + decisão cognitiva."""
    import json as json_lib

    pdf = request.FILES.get("pdf")
    if not pdf:
        return JsonResponse({"ok": False, "error": "Campo pdf obrigatório"}, status=400)
    if not pdf.name.lower().endswith(".pdf"):
        return JsonResponse({"ok": False, "error": "Apenas arquivos .pdf"}, status=400)

    max_mb = int(os.environ.get("RAG_GASTR_PDF_MAX_MB", "40") or 40)
    max_bytes = max(1, max_mb) * 1024 * 1024
    size = getattr(pdf, "size", None) or 0
    if size and size > max_bytes:
        return JsonResponse({"ok": False, "error": f"PDF acima do limite ({max_mb} MB)"}, status=400)

    try:
        cw = int(request.POST.get("chunk_words") or 400)
    except (TypeError, ValueError):
        cw = 400
    cw = max(80, min(1200, cw))

    preview_id = str(uuid.uuid4())
    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
    try:
        for chunk in pdf.chunks():
            tmp.write(chunk)
        tmp.close()
        from core.services.ingestion.pdf_ingestor import extract_pdf_chunks_only

        ext = extract_pdf_chunks_only(tmp.name, chunk_words=cw)
        if not ext.get("ok"):
            return JsonResponse(
                {"ok": False, "error": ext.get("error") or "Extração falhou"},
                status=400,
            )

        preview_dir = Path(settings.MEDIA_ROOT) / "rag_preview"
        preview_dir.mkdir(parents=True, exist_ok=True)
        payload = {
            "preview_id": preview_id,
            "source_name": pdf.name,
            "chunk_words": cw,
            "chunks": ext["chunks"],
            "pages": ext["pages"],
            "truncated": ext.get("truncated"),
        }
        pjson = preview_dir / f"{preview_id}.json"
        with open(pjson, "w", encoding="utf-8") as f:
            json_lib.dump(payload, f, ensure_ascii=False)
    except Exception as e:
        logger.exception("rag_gastronomico_preview")
        try:
            os.unlink(tmp.name)
        except OSError:
            pass
        return JsonResponse({"ok": False, "error": str(e)}, status=500)
    else:
        try:
            os.unlink(tmp.name)
        except OSError:
            pass

    decision = _rag_gastro_decision_preview(
        filename=pdf.name,
        chunk_count=int(ext.get("chunk_count") or 0),
        pages=int(ext.get("pages") or 0),
    )

    rows = []
    for i, ch in enumerate(ext.get("chunks") or []):
        t = ch.get("text") or ""
        rows.append(
            {
                "index": i,
                "type": ch.get("type") or "conceito",
                "snippet": (t[:360] + "…") if len(t) > 360 else t,
            }
        )

    return JsonResponse(
        {
            "ok": True,
            "preview_id": preview_id,
            "pages": ext.get("pages"),
            "chunk_count": ext.get("chunk_count"),
            "truncated": ext.get("truncated"),
            "chunk_words": cw,
            "chunks": rows,
            "decision": decision,
        }
    )


@require_POST
def rag_gastronomico_commit(request):
    """Indexa no vectorstore os chunks escolhidos a partir de um preview_id."""
    import json as json_lib

    try:
        body = json_lib.loads((request.body or b"").decode() or "{}")
    except json_lib.JSONDecodeError:
        return JsonResponse({"ok": False, "error": "JSON inválido"}, status=400)

    preview_id = str(body.get("preview_id") or "").strip()
    has_indices_key = "indices" in body
    indices = body.get("indices")
    try:
        uuid.UUID(preview_id)
    except (ValueError, TypeError):
        return JsonResponse({"ok": False, "error": "preview_id inválido"}, status=400)

    pjson = Path(settings.MEDIA_ROOT) / "rag_preview" / f"{preview_id}.json"
    if not pjson.is_file():
        return JsonResponse({"ok": False, "error": "Preview expirado ou inexistente"}, status=404)

    try:
        with open(pjson, encoding="utf-8") as f:
            payload = json_lib.load(f)
    except Exception as e:
        return JsonResponse({"ok": False, "error": f"Ficheiro preview inválido: {e}"}, status=500)

    chunks_full = payload.get("chunks") or []
    source = str(payload.get("source_name") or "preview")

    selected_texts: List[str] = []
    if not has_indices_key or indices is None:
        for c in chunks_full:
            if isinstance(c, dict) and (c.get("text") or "").strip():
                selected_texts.append(str(c["text"]).strip())
    elif isinstance(indices, list):
        if len(indices) == 0:
            return JsonResponse(
                {"ok": False, "error": "Lista indices vazia — selecione pelo menos um chunk"},
                status=400,
            )
        for i in indices:
            try:
                idx = int(i)
            except (TypeError, ValueError):
                continue
            if 0 <= idx < len(chunks_full):
                txt = (chunks_full[idx].get("text") if isinstance(chunks_full[idx], dict) else "") or ""
                if txt.strip():
                    selected_texts.append(txt.strip())
    else:
        return JsonResponse({"ok": False, "error": "indices deve ser uma lista ou omitido"}, status=400)

    if not selected_texts:
        return JsonResponse({"ok": False, "error": "Nenhum chunk selecionado para indexar"}, status=400)

    from core.services.ingestion.pdf_ingestor import ID_PREFIX, ingest_chunk_strings

    r = ingest_chunk_strings(selected_texts, source=source, domain="gastronomia", id_prefix=ID_PREFIX)
    try:
        if pjson.is_file():
            pjson.unlink()
    except OSError:
        pass

    return JsonResponse(
        {
            "ok": True,
            "chunks_ingested": r.get("chunks_ingested"),
            "chunks_total": len(selected_texts),
            "errors": r.get("errors") or [],
            "id_prefix": ID_PREFIX,
            "source": source,
        }
    )
