"""
Views DRF para Creative Engine API
"""
import logging
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from services.creative_engine_service.engine import CreativeEngine
from services.creative_engine_service.contracts import CreativeContext
from services.creative_engine_service.adapters.whatsapp import WhatsAppAdapter
from app_creative_engine.api.serializers import (
    GenerateCreativeSerializer,
    GenerateVariantsSerializer,
    AdaptCreativeSerializer,
    PerformanceEventSerializer,
    RecommendNextSerializer,
)

logger = logging.getLogger(__name__)

# Instância singleton do engine
_engine = None


def get_engine():
    """Retorna instância do engine (singleton)"""
    global _engine
    if _engine is None:
        _engine = CreativeEngine()
    return _engine


@api_view(['POST'])
@permission_classes([AllowAny])
def generate_creative(request):
    """
    POST /api/creative-engine/generate
    Gera criativo principal
    """
    serializer = GenerateCreativeSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    
    engine = get_engine()
    
    # Construir contexto
    context = CreativeContext(
        channel=serializer.validated_data['channel'],
        locale=serializer.validated_data.get('locale', 'pt-BR'),
        tone=serializer.validated_data.get('tone', 'direto'),
        audience_hint=serializer.validated_data.get('audience_hint'),
        time_of_day=serializer.validated_data.get('time_of_day'),
        stock_level=serializer.validated_data.get('stock_level'),
        price_sensitivity=serializer.validated_data.get('price_sensitivity'),
        campaign_tag=serializer.validated_data.get('campaign_tag'),
    )
    
    try:
        result = engine.generate_creative(
            product_id=serializer.validated_data['product_id'],
            shopper_id=serializer.validated_data['shopper_id'],
            context=context
        )
        
        # Converter para dict
        response_data = {
            "creative_id": result.creative_id,
            "variants": [
                {
                    "variant_id": v.variant_id,
                    "strategy": v.strategy,
                    "channel": v.channel,
                    "image_url": v.image_url,
                    "text_short": v.text_short,
                    "text_medium": v.text_medium,
                    "text_long": v.text_long,
                    "discourse": v.discourse,
                    "ctas": v.ctas,
                }
                for v in result.variants
            ],
            "recommended_variant_id": result.recommended_variant_id,
        }
        
        if result.debug:
            response_data["debug"] = result.debug
        
        return Response(response_data, status=status.HTTP_201_CREATED)
        
    except Exception as e:
        logger.error(f"Erro ao gerar criativo: {e}", exc_info=True)
        return Response(
            {"error": str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
@permission_classes([AllowAny])
def generate_variants(request, creative_id):
    """
    POST /api/creative-engine/{creative_id}/variants
    Gera variantes de um criativo
    """
    serializer = GenerateVariantsSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    
    engine = get_engine()
    
    context = CreativeContext(
        channel=serializer.validated_data['channel'],
        locale=serializer.validated_data.get('locale', 'pt-BR'),
        tone=serializer.validated_data.get('tone', 'direto'),
    )
    
    try:
        variants = engine.generate_variants(
            creative_id=creative_id,
            strategies=serializer.validated_data['strategies'],
            context=context
        )
        
        response_data = [
            {
                "variant_id": v.variant_id,
                "strategy": v.strategy,
                "channel": v.channel,
                "image_url": v.image_url,
                "text_short": v.text_short,
                "text_medium": v.text_medium,
                "text_long": v.text_long,
                "discourse": v.discourse,
                "ctas": v.ctas,
            }
            for v in variants
        ]
        
        return Response(response_data, status=status.HTTP_201_CREATED)
        
    except Exception as e:
        logger.error(f"Erro ao gerar variantes: {e}", exc_info=True)
        return Response(
            {"error": str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
@permission_classes([AllowAny])
def adapt_creative(request, variant_id):
    """
    POST /api/creative-engine/variants/{variant_id}/adapt
    Adapta variante para canal
    """
    serializer = AdaptCreativeSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    
    engine = get_engine()
    adapter = WhatsAppAdapter()
    
    context = CreativeContext(
        channel=serializer.validated_data['channel'],
        locale=serializer.validated_data.get('locale', 'pt-BR'),
        tone=serializer.validated_data.get('tone', 'direto'),
    )
    
    try:
        result = engine.adapt_creative(
            variant_id=variant_id,
            channel=serializer.validated_data['channel'],
            context=context
        )
        
        return Response(result, status=status.HTTP_200_OK)
        
    except Exception as e:
        logger.error(f"Erro ao adaptar criativo: {e}", exc_info=True)
        return Response(
            {"error": str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
@permission_classes([AllowAny])
def register_performance(request):
    """
    POST /api/creative-engine/performance
    Registra evento de performance
    """
    serializer = PerformanceEventSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    
    engine = get_engine()
    
    try:
        engine.register_performance(serializer.validated_data)
        return Response({"success": True}, status=status.HTTP_200_OK)
        
    except Exception as e:
        logger.error(f"Erro ao registrar performance: {e}", exc_info=True)
        return Response(
            {"error": str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([AllowAny])
def recommend_next(request):
    """
    GET /api/creative-engine/recommend?shopper_id=...&product_id=...&channel=...
    Recomenda próximo criativo
    """
    serializer = RecommendNextSerializer(data=request.query_params)
    serializer.is_valid(raise_exception=True)
    
    engine = get_engine()
    
    context = CreativeContext(
        channel=serializer.validated_data['channel'],
        locale=serializer.validated_data.get('locale', 'pt-BR'),
        tone=serializer.validated_data.get('tone', 'direto'),
    )
    
    try:
        result = engine.recommend_next(
            shopper_id=serializer.validated_data['shopper_id'],
            product_id=serializer.validated_data['product_id'],
            context=context
        )
        
        response_data = {
            "creative_id": result.creative_id,
            "variants": [
                {
                    "variant_id": v.variant_id,
                    "strategy": v.strategy,
                    "channel": v.channel,
                    "image_url": v.image_url,
                    "text_short": v.text_short,
                    "text_medium": v.text_medium,
                    "text_long": v.text_long,
                    "discourse": v.discourse,
                    "ctas": v.ctas,
                }
                for v in result.variants
            ],
            "recommended_variant_id": result.recommended_variant_id,
        }
        
        if result.debug:
            response_data["debug"] = result.debug
        
        return Response(response_data, status=status.HTTP_200_OK)
        
    except Exception as e:
        logger.error(f"Erro ao recomendar criativo: {e}", exc_info=True)
        return Response(
            {"error": str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
