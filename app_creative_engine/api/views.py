"""
Views da API do Creative Engine
"""
import uuid
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
import json

from app_creative_engine.models import CreativeAsset, CreativePerformance, CreativeScore


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
