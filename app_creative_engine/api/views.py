"""
Views da API do Creative Engine
"""
import uuid
import os
import tempfile
import subprocess
from pathlib import Path
from django.shortcuts import render
from django.http import JsonResponse, HttpResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
import json

from app_creative_engine.models import (
    CreativeAsset,
    CreativePerformance,
    CreativeScore,
    CreativeJob,
    CreativeJobOutput,
)


@csrf_exempt
@require_http_methods(["POST"])
def generate_creative(request):
    """
    Gera um novo criativo
    POST /api/creative-engine/generate
    """
    try:
        data = json.loads(request.body) if request.body else {}
        
        creative_id = str(uuid.uuid4())
        variant_id = str(uuid.uuid4())
        product_id = data.get('product_id', '')
        shopper_id = data.get('shopper_id')
        channel = data.get('channel', 'whatsapp')
        strategy = data.get('strategy', 'default')
        
        # Criar asset básico
        asset = CreativeAsset.objects.create(
            creative_id=creative_id,
            variant_id=variant_id,
            product_id=product_id,
            shopper_id=shopper_id,
            channel=channel,
            strategy=strategy,
            image_url=data.get('image_url'),
            text_short=data.get('text_short'),
            text_medium=data.get('text_medium'),
            text_long=data.get('text_long'),
            discourse=data.get('discourse', {}),
            ctas=data.get('ctas', [])
        )
        
        return JsonResponse({
            'creative_id': creative_id,
            'variant_id': variant_id,
            'status': 'created'
        }, status=201)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)


@csrf_exempt
@require_http_methods(["POST"])
def generate_variants(request, creative_id):
    """
    Gera variantes de um criativo
    POST /api/creative-engine/{creative_id}/variants
    """
    try:
        data = json.loads(request.body) if request.body else {}
        count = data.get('count', 1)
        
        variants = []
        for i in range(count):
            variant_id = str(uuid.uuid4())
            # Buscar criativo original para copiar dados
            original = CreativeAsset.objects.filter(creative_id=creative_id).first()
            
            if original:
                variant = CreativeAsset.objects.create(
                    creative_id=creative_id,
                    variant_id=variant_id,
                    product_id=original.product_id,
                    shopper_id=original.shopper_id,
                    channel=original.channel,
                    strategy=original.strategy,
                    image_url=data.get('image_url') or original.image_url,
                    text_short=data.get('text_short') or original.text_short,
                    text_medium=data.get('text_medium') or original.text_medium,
                    text_long=data.get('text_long') or original.text_long,
                    discourse=data.get('discourse', original.discourse),
                    ctas=data.get('ctas', original.ctas)
                )
                variants.append(variant_id)
        
        return JsonResponse({
            'creative_id': creative_id,
            'variants': variants,
            'count': len(variants)
        }, status=201)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)


@csrf_exempt
@require_http_methods(["POST"])
def adapt_creative(request, variant_id):
    """
    Adapta um criativo existente
    POST /api/creative-engine/variants/{variant_id}/adapt
    """
    try:
        data = json.loads(request.body) if request.body else {}
        
        variant = CreativeAsset.objects.filter(variant_id=variant_id).first()
        if not variant:
            return JsonResponse({'error': 'Variant not found'}, status=404)
        
        # Atualizar campos se fornecidos
        if 'image_url' in data:
            variant.image_url = data['image_url']
        if 'text_short' in data:
            variant.text_short = data['text_short']
        if 'text_medium' in data:
            variant.text_medium = data['text_medium']
        if 'text_long' in data:
            variant.text_long = data['text_long']
        if 'discourse' in data:
            variant.discourse = data['discourse']
        if 'ctas' in data:
            variant.ctas = data['ctas']
        
        variant.save()
        
        return JsonResponse({
            'variant_id': variant_id,
            'status': 'adapted'
        }, status=200)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)


@csrf_exempt
@require_http_methods(["POST"])
def register_performance(request):
    """
    Registra performance de um criativo
    POST /api/creative-engine/performance
    """
    try:
        data = json.loads(request.body) if request.body else {}
        
        performance = CreativePerformance.objects.create(
            variant_id=data.get('variant_id', ''),
            creative_id=data.get('creative_id', ''),
            product_id=data.get('product_id', ''),
            shopper_id=data.get('shopper_id'),
            event_type=data.get('event_type', 'view'),
            event_data=data.get('event_data', {}),
            correlation_id=data.get('correlation_id')
        )
        
        return JsonResponse({
            'id': str(performance.id),
            'status': 'registered'
        }, status=201)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)


@csrf_exempt
@require_http_methods(["GET", "POST"])
def recommend_next(request):
    """
    Recomenda próximo criativo
    GET/POST /api/creative-engine/recommend
    """
    try:
        if request.method == 'GET':
            params = request.GET
        else:
            data = json.loads(request.body) if request.body else {}
            params = data
        
        product_id = params.get('product_id', '')
        shopper_id = params.get('shopper_id')
        channel = params.get('channel', 'whatsapp')
        
        # Buscar melhor score para o produto/canal
        best_score = CreativeScore.objects.filter(
            product_id=product_id,
            channel=channel
        ).order_by('-engagement_score').first()
        
        if best_score:
            # Buscar asset correspondente
            asset = CreativeAsset.objects.filter(
                variant_id=best_score.variant_id
            ).first()
            
            if asset:
                return JsonResponse({
                    'recommended_variant_id': best_score.variant_id,
                    'creative_id': best_score.creative_id,
                    'engagement_score': best_score.engagement_score,
                    'strategy': best_score.strategy,
                    'asset': {
                        'image_url': asset.image_url,
                        'text_short': asset.text_short,
                        'text_medium': asset.text_medium,
                        'text_long': asset.text_long
                    }
                }, status=200)
        
        return JsonResponse({
            'message': 'No recommendations available',
            'recommended_variant_id': None
        }, status=200)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)


# =============================================================================
# Jobs de criação (fluxo Kwai/Tamo - documento CREATIVE_ENGINE_ANALYSIS)
# =============================================================================

@csrf_exempt
@require_http_methods(["POST"])
def create_job(request):
    """
    Cria job de criação - upload de imagem para processamento em background.
    POST /api/creative-engine/jobs/
    Body: multipart/form-data com 'image' (arquivo) ou JSON com image_url
    """
    try:
        shopper_id = request.POST.get('shopper_id') or request.GET.get('shopper_id')
        product_id = request.POST.get('product_id') or request.GET.get('product_id')

        image_path = None
        image_url = None

        if request.FILES.get('image'):
            f = request.FILES['image']
            media_root = Path(getattr(settings, 'MEDIA_ROOT', 'media'))
            upload_dir = media_root / 'uploads' / 'creative'
            upload_dir.mkdir(parents=True, exist_ok=True)
            ext = Path(f.name).suffix or '.jpg'
            filename = f"{uuid.uuid4()}{ext}"
            filepath = upload_dir / filename
            with open(filepath, 'wb') as dest:
                for chunk in f.chunks():
                    dest.write(chunk)
            # Path relativo para o worker encontrar (BASE_DIR / image_path)
            base_dir = Path(getattr(settings, 'BASE_DIR', '.'))
            try:
                image_path = str(filepath.relative_to(base_dir))
            except ValueError:
                image_path = str(filepath)
            if getattr(settings, 'MEDIA_URL', ''):
                image_url = f"{settings.MEDIA_URL}uploads/creative/{filename}"

        elif request.content_type and 'application/json' in request.content_type:
            data = json.loads(request.body) if request.body else {}
            image_url = data.get('image_url')
            image_path = data.get('image_path')
            shopper_id = shopper_id or data.get('shopper_id')
            product_id = product_id or data.get('product_id')

        if not image_path and not image_url:
            return JsonResponse({'error': 'Envie uma imagem (campo image) ou image_url'}, status=400)

        if not image_path and image_url:
            image_path = image_url

        job = CreativeJob.objects.create(
            shopper_id=shopper_id,
            product_id=product_id,
            image_path=image_path,
            image_url=image_url,
            status='queued',
        )

        # Enfileirar processamento
        try:
            from app_creative_engine.tasks import process_creative_job
            process_creative_job.delay(str(job.id))
        except Exception as e:
            job.status = 'failed'
            job.error_message = f'Erro ao enfileirar: {e}'
            job.save()
            return JsonResponse({'error': str(e)}, status=500)

        return JsonResponse({
            'job_id': str(job.id),
            'status': 'queued',
            'message': 'Job criado. Use GET /api/creative-engine/jobs/{job_id}/ para acompanhar.',
        }, status=201)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)


@require_http_methods(["GET"])
def job_status(request, job_id):
    """
    Retorna status do job.
    GET /api/creative-engine/jobs/{job_id}/
    """
    try:
        job = CreativeJob.objects.get(id=job_id)
        return JsonResponse({
            'job_id': str(job.id),
            'status': job.status,
            'stage': job.stage,
            'progress': job.progress,
            'description': job.description,
            'error_message': job.error_message,
            'created_at': job.created_at.isoformat(),
            'completed_at': job.completed_at.isoformat() if job.completed_at else None,
        })
    except CreativeJob.DoesNotExist:
        return JsonResponse({'error': 'Job não encontrado'}, status=404)


@require_http_methods(["GET"])
def job_outputs(request, job_id):
    """
    Retorna outputs gerados pelo job.
    GET /api/creative-engine/jobs/{job_id}/outputs/
    """
    try:
        job = CreativeJob.objects.get(id=job_id)
        outputs = list(
            CreativeJobOutput.objects.filter(job=job).values(
                'id', 'style', 'template_id', 'image_url', 'thumbnail_url', 'metadata', 'created_at'
            )
        )
        for o in outputs:
            o['created_at'] = o['created_at'].isoformat() if o.get('created_at') else None
        return JsonResponse({
            'job_id': str(job.id),
            'status': job.status,
            'outputs': outputs,
        })
    except CreativeJob.DoesNotExist:
        return JsonResponse({'error': 'Job não encontrado'}, status=404)


# Opções de enriquecimento com IA para o template
PDF_ENRICH_INSTRUCTIONS = [
    ("melhorar_ebook", "Melhorar para ebook"),
    ("resumo_executivo", "Adicionar resumo executivo"),
    ("revisar_pt", "Revisar português"),
]

# Layouts de PDF (formatação) – valor enviado no form → argumentos extras do Pandoc
PDF_LAYOUTS = [
    ("plain", "Simples (A4, margens padrão)"),
    ("ebook", "Ebook (leitura confortável, fonte 12pt)"),
    ("relatorio", "Relatório (cabeçalho e rodapé com numeração)"),
    ("apresentacao", "Apresentação (fonte maior, margens amplas)"),
    ("guia_tecnico", "Guia técnico (tema escuro, títulos em destaque, código estilizado)"),
    ("layout_pi", "Layout PI (tema roxo/dourado, estilo Pi Network)"),
]


def _get_pandoc_layout_args(layout_key: str) -> list:
    """Retorna lista de argumentos extras para o Pandoc conforme o layout escolhido."""
    base_dir = Path(getattr(settings, "BASE_DIR", "."))
    templates_dir = base_dir / "app_creative_engine" / "pandoc_templates"

    if layout_key == "plain":
        return ["-V", "fontsize=11pt", "-V", "papersize=a4"]
    if layout_key == "ebook":
        return [
            "-V", "fontsize=12pt",
            "-V", "geometry=top=2.5cm,bottom=2.5cm,left=2.5cm,right=2.5cm",
            "-V", "linestretch=1.25",
        ]
    if layout_key == "relatorio":
        header_path = templates_dir / "relatorio_header.tex"
        if header_path.exists():
            return ["-V", "fontsize=11pt", "-V", "papersize=a4", "--include-in-header", str(header_path)]
        return ["-V", "fontsize=11pt", "-V", "papersize=a4"]
    if layout_key == "apresentacao":
        return [
            "-V", "fontsize=14pt",
            "-V", "geometry=margin=2.5cm",
            "-V", "linestretch=1.2",
        ]
    if layout_key == "guia_tecnico":
        header_path = templates_dir / "guia_tecnico_header.tex"
        args = ["-V", "fontsize=11pt", "-V", "papersize=a4", "--toc"]
        if header_path.exists():
            args.extend(["--include-in-header", str(header_path)])
        return args
    if layout_key == "layout_pi":
        header_path = templates_dir / "layout_pi_header.tex"
        args = ["-V", "fontsize=11pt", "-V", "papersize=a4", "--toc"]
        if header_path.exists():
            args.extend(["--include-in-header", str(header_path)])
        return args
    return ["-V", "fontsize=11pt", "-V", "papersize=a4"]


@csrf_exempt
@require_http_methods(["GET", "POST"])
def generate_pdf_from_markdown(request):
    """
    Tela + endpoint para gerar PDF:
    - A partir de um ou mais arquivos .md (upload), ou
    - A partir de um brief (título, corpo, CTA).
    Opcional: enriquecer texto com IA (OpenMind) antes de gerar o PDF.
    """
    context = {
        "pdf_url": None,
        "error": None,
        "enrich_failed": False,
        "enrich_instructions": PDF_ENRICH_INSTRUCTIONS,
        "pdf_layouts": PDF_LAYOUTS,
    }

    if request.method != "POST":
        context["enrich_instructions"] = PDF_ENRICH_INSTRUCTIONS
        context["pdf_layouts"] = PDF_LAYOUTS
        return render(request, "app_creative_engine/md_to_pdf.html", context)

    try:
        markdown = None
        files = request.FILES.getlist("files")
        headline = (request.POST.get("headline") or "").strip()
        body = (request.POST.get("body") or "").strip()
        cta = (request.POST.get("cta") or "Saiba mais").strip()
        use_brief = bool(headline or body)

        if use_brief:
            parts = []
            if headline:
                parts.append(f"# {headline}\n\n")
            if body:
                parts.append(body)
                if not body.endswith("\n"):
                    parts.append("\n")
            if cta:
                parts.append(f"\n\n---\n\n*{cta}*\n")
            markdown = "".join(parts) if parts else None
            if not markdown:
                context["error"] = "Preencha pelo menos o título ou o corpo do brief."
                return render(request, "app_creative_engine/md_to_pdf.html", context)
        elif files:
            markdown_parts = []
            for f in files:
                content = f.read().decode("utf-8")
                markdown_parts.append(f"# {f.name}\n\n")
                markdown_parts.append(content)
                markdown_parts.append("\n\n---\n\n")
            markdown = "".join(markdown_parts)
        else:
            context["error"] = "Envie um ou mais arquivos .md ou preencha o brief (título/corpo)."
            return render(request, "app_creative_engine/md_to_pdf.html", context)

        # Enriquecimento opcional com OpenMind
        if request.POST.get("enrich_with_ai"):
            try:
                from services.creative_engine_service.document import enrich_markdown_with_ai
                instruction = request.POST.get("enrich_instruction", "melhorar_ebook")
                custom = (request.POST.get("enrich_custom_prompt") or "").strip()
                enriched = enrich_markdown_with_ai(
                    markdown,
                    instruction=instruction,
                    custom_prompt=custom or None,
                )
                if enriched:
                    markdown = enriched
                else:
                    context["enrich_failed"] = True
            except Exception:
                context["enrich_failed"] = True

        with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as tmp_md:
            tmp_md.write(markdown)
            tmp_md_path = tmp_md.name

        media_root = Path(getattr(settings, "MEDIA_ROOT", "media"))
        output_dir = media_root / "creative_docs"
        output_dir.mkdir(parents=True, exist_ok=True)

        pdf_name = f"md_{uuid.uuid4()}.pdf"
        output_path = output_dir / pdf_name

        cmd = [
            "pandoc",
            tmp_md_path,
            "-o",
            str(output_path),
            "--pdf-engine=xelatex",
        ]
        layout_key = (request.POST.get("pdf_layout") or "plain").strip()
        cmd.extend(_get_pandoc_layout_args(layout_key))

        result = subprocess.run(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )

        if result.returncode != 0:
            context["error"] = f"Pandoc falhou: {result.stderr}"
        else:
            media_url = getattr(settings, "MEDIA_URL", "/media/")
            if not media_url.endswith("/"):
                media_url += "/"
            context["pdf_url"] = f"{media_url}creative_docs/{pdf_name}"
    except Exception as exc:
        context["error"] = str(exc)

    context["enrich_instructions"] = PDF_ENRICH_INSTRUCTIONS
    context["pdf_layouts"] = PDF_LAYOUTS
    return render(request, "app_creative_engine/md_to_pdf.html", context)


# -----------------------------------------------------------------------------
# Geração de imagens por IA (descrição e/ou imagem modelo)
# -----------------------------------------------------------------------------

@csrf_exempt
@require_http_methods(["GET", "POST"])
def generate_image_from_prompt(request):
    """
    Gera imagem por IA a partir de uma descrição (e opcionalmente uma imagem modelo).
    GET  → formulário
    POST → prompt (obrigatório), opcional: image (arquivo) para modo edição.
    """
    context = {"image_url": None, "error": None}

    if request.method == "POST":
        prompt = (request.POST.get("prompt") or "").strip()
        if not prompt:
            context["error"] = "Informe a descrição da imagem (campo prompt)."
        else:
            size = request.POST.get("size") or "1024x1024"
            quality = request.POST.get("quality") or "standard"
            style = request.POST.get("style") or "vivid"

            ref_file = request.FILES.get("image")
            if ref_file:
                # Modo edição: imagem modelo + prompt
                media_root = Path(getattr(settings, "MEDIA_ROOT", "media"))
                upload_dir = media_root / "creative_images" / "uploads"
                upload_dir.mkdir(parents=True, exist_ok=True)
                ref_path = upload_dir / f"ref_{uuid.uuid4().hex[:8]}{Path(ref_file.name).suffix or '.png'}"
                with open(ref_path, "wb") as f:
                    for chunk in ref_file.chunks():
                        f.write(chunk)
                try:
                    from services.creative_engine_service.generators.ai_image_generator import (
                        generate_image_from_reference,
                    )
                    file_path, err = generate_image_from_reference(str(ref_path), prompt)
                finally:
                    try:
                        ref_path.unlink(missing_ok=True)
                    except Exception:
                        pass
            else:
                # Modo texto: só descrição
                try:
                    from services.creative_engine_service.generators.ai_image_generator import (
                        generate_image_from_prompt as gen,
                    )
                    file_path, err = gen(
                        prompt=prompt,
                        size=size,
                        quality=quality,
                        style=style,
                    )
                except Exception as e:
                    file_path, err = None, str(e)

            if err:
                context["error"] = err
            elif file_path:
                media_root = Path(getattr(settings, "MEDIA_ROOT", "media"))
                try:
                    rel = Path(file_path).relative_to(media_root)
                except ValueError:
                    rel = Path(file_path).name
                media_url = getattr(settings, "MEDIA_URL", "/media/")
                if not media_url.endswith("/"):
                    media_url += "/"
                context["image_url"] = f"{media_url}{rel}"

    return render(request, "app_creative_engine/image_from_prompt.html", context)


# -----------------------------------------------------------------------------
# Geração de vídeos por IA (Sora / OpenAI)
# -----------------------------------------------------------------------------

@csrf_exempt
@require_http_methods(["GET", "POST"])
def generate_video_from_prompt(request):
    """
    Gera vídeo por IA a partir de uma descrição (Sora).
    GET  → formulário
    POST → prompt (obrigatório), model, size, seconds.
    """
    context = {"video_url": None, "error": None}

    if request.method == "POST":
        prompt = (request.POST.get("prompt") or "").strip()
        if not prompt:
            context["error"] = "Informe a descrição do vídeo (campo prompt)."
        else:
            model = request.POST.get("model") or "sora-2"
            size = request.POST.get("size") or "1280x720"
            seconds = request.POST.get("seconds") or "8"
            try:
                from services.creative_engine_service.generators.ai_video_generator import (
                    generate_video_from_prompt as gen_video,
                )
                file_path, err = gen_video(
                    prompt=prompt,
                    model=model,
                    size=size,
                    seconds=seconds,
                )
            except Exception as e:
                file_path, err = None, str(e)

            if err:
                context["error"] = err
            elif file_path:
                media_root = Path(getattr(settings, "MEDIA_ROOT", "media"))
                try:
                    rel = Path(file_path).relative_to(media_root)
                except ValueError:
                    rel = Path(file_path).name
                media_url = getattr(settings, "MEDIA_URL", "/media/")
                if not media_url.endswith("/"):
                    media_url += "/"
                context["video_url"] = f"{media_url}{rel}"

    return render(request, "app_creative_engine/video_from_prompt.html", context)


# -----------------------------------------------------------------------------
# Geração de áudio por IA (TTS — texto → fala)
# -----------------------------------------------------------------------------

@csrf_exempt
@require_http_methods(["GET", "POST"])
def generate_audio_from_text(request):
    """
    Narração sintética a partir de texto (OpenAI TTS).
    GET  → formulário
    POST → text (obrigatório), voice, model, speed.
    """
    context = {"audio_url": None, "error": None}

    if request.method == "POST":
        text = (request.POST.get("text") or "").strip()
        if not text:
            context["error"] = "Informe o texto a ser narrado."
        else:
            voice = request.POST.get("voice") or "nova"
            model = request.POST.get("model") or "tts-1-hd"
            try:
                speed = float(request.POST.get("speed") or "1.0")
            except (TypeError, ValueError):
                speed = 1.0
            try:
                from services.creative_engine_service.generators.ai_audio_generator import (
                    generate_speech_from_text,
                )
                file_path, err = generate_speech_from_text(
                    text=text,
                    voice=voice,
                    model=model,
                    speed=speed,
                )
            except Exception as e:
                file_path, err = None, str(e)

            if err:
                context["error"] = err
            elif file_path:
                media_root = Path(getattr(settings, "MEDIA_ROOT", "media"))
                try:
                    rel = Path(file_path).relative_to(media_root)
                except ValueError:
                    rel = Path(file_path).name
                media_url = getattr(settings, "MEDIA_URL", "/media/")
                if not media_url.endswith("/"):
                    media_url += "/"
                context["audio_url"] = f"{media_url}{rel}"

    return render(request, "app_creative_engine/audio_from_text.html", context)
