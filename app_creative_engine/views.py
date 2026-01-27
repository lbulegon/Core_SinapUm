"""
Views do Creative Engine - Interface de Teste
"""
from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from .models import CreativeAsset, CreativePerformance, CreativeScore
import json


@require_http_methods(["GET"])
def test_creative_engine(request):
    """
    Interface de teste do Creative Engine
    GET /api/creative-engine/test/
    """
    # Buscar alguns exemplos para exibir
    recent_assets = CreativeAsset.objects.all()[:10]
    recent_performances = CreativePerformance.objects.all()[:10]
    top_scores = CreativeScore.objects.all()[:10]
    
    context = {
        'recent_assets': recent_assets,
        'recent_performances': recent_performances,
        'top_scores': top_scores,
    }
    
    return render(request, 'app_creative_engine/test.html', context)


@csrf_exempt
@require_http_methods(["GET"])
def list_creatives(request):
    """
    Lista todos os criativos
    GET /api/creative-engine/list/
    """
    try:
        assets = CreativeAsset.objects.all().order_by('-created_at')[:50]
        
        result = []
        for asset in assets:
            result.append({
                'creative_id': asset.creative_id,
                'variant_id': asset.variant_id,
                'product_id': asset.product_id,
                'shopper_id': asset.shopper_id,
                'channel': asset.channel,
                'strategy': asset.strategy,
                'image_url': asset.image_url,
                'text_short': asset.text_short,
                'text_medium': asset.text_medium,
                'text_long': asset.text_long,
                'created_at': asset.created_at.isoformat(),
            })
        
        return JsonResponse({
            'success': True,
            'count': len(result),
            'creatives': result
        })
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)
