from django.shortcuts import render, redirect
from django.contrib import messages
from django.views.decorators.http import require_http_methods
from django.conf import settings
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .services import analyze_image_with_openmind, analyze_multiple_images
from .models import ProdutoJSON
import json
import os
import uuid
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

def home(request):
    """View para a página inicial com menu."""
    context = {
        'grafana_url': 'http://69.169.102.84:3000/login',
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
            
            # Transformar e adicionar caminho da imagem
            from .utils import transform_evora_to_modelo_json
            if produto_data and result.get('success'):
                if 'produto' not in produto_data or 'produto_generico_catalogo' not in produto_data:
                    produto_data = transform_evora_to_modelo_json(
                        produto_data,
                        image_filename=image_file.name,
                        image_path=image_path
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
