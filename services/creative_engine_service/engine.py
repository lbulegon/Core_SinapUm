"""
Orquestrador principal do Creative Engine
"""
import logging
import uuid
from typing import Dict, Any, List, Optional
from django.core.exceptions import ObjectDoesNotExist

from services.creative_engine_service.contracts import (
    CreativeContext,
    CreativeResponse,
    CreativeVariant,
    CreativeBrief,
)
from services.creative_engine_service.events import (
    CreativeEventType,
    emit_creative_event,
)
from services.creative_engine_service.generators.text import TextGenerator
from services.creative_engine_service.generators.discourse import DiscourseGenerator
from services.creative_engine_service.generators.image import ImageGenerator
from services.creative_engine_service.strategies.price import PriceStrategy
from services.creative_engine_service.strategies.benefit import BenefitStrategy
from services.creative_engine_service.strategies.urgency import UrgencyStrategy
from services.creative_engine_service.strategies.scarcity import ScarcityStrategy
from services.creative_engine_service.strategies.social_proof import SocialProofStrategy
from services.creative_engine_service.learning.optimizer import CreativeOptimizer

logger = logging.getLogger(__name__)


class CreativeEngine:
    """Orquestrador principal do Creative Engine"""
    
    def __init__(self):
        """Inicializa geradores e estratégias"""
        self.text_generator = TextGenerator()
        self.discourse_generator = DiscourseGenerator()
        self.image_generator = ImageGenerator()
        
        self.strategies = {
            "price": PriceStrategy(),
            "benefit": BenefitStrategy(),
            "urgency": UrgencyStrategy(),
            "scarcity": ScarcityStrategy(),
            "social_proof": SocialProofStrategy(),
        }
        
        self.optimizer = CreativeOptimizer()
    
    def generate_creative(
        self,
        product_id: str,
        shopper_id: str,
        context: CreativeContext,
        product_data: Optional[Dict[str, Any]] = None
    ) -> CreativeResponse:
        """
        Gera criativo principal para produto e shopper
        
        Args:
            product_id: ID do produto
            shopper_id: ID do shopper
            context: Contexto de geração
            product_data: Dados do produto (opcional - se não fornecido, tenta buscar no banco)
        
        Returns:
            CreativeResponse com criativo e variantes
        """
        correlation_id = str(uuid.uuid4())
        
        try:
            # Se product_data foi fornecido, usar diretamente; caso contrário, buscar no banco
            if product_data is None:
                product_data = self._get_product_data(product_id)
            else:
                # Garantir que product_data tem o formato esperado
                product_data = self._normalize_product_data(product_data, product_id)
            
            # Gerar variantes com estratégias padrão
            default_strategies = ["price", "benefit", "urgency"]
            variants = self._generate_variants(
                product_data=product_data,
                strategies=default_strategies,
                context=context,
                correlation_id=correlation_id
            )
            
            # Otimizar recomendações
            variants = self.optimizer.optimize_recommendations(
                variants=variants,
                context=context
            )
            
            creative_id = str(uuid.uuid4())
            recommended_variant_id = variants[0].variant_id if variants else None
            
            # Emitir evento
            emit_creative_event(
                event_type=CreativeEventType.CREATIVE_GENERATED,
                data={
                    "product_id": product_id,
                    "variants_count": len(variants),
                    "recommended_variant": recommended_variant_id,
                },
                shopper_id=shopper_id,
                product_id=product_id,
                creative_id=creative_id,
                correlation_id=correlation_id
            )
            
            return CreativeResponse(
                creative_id=creative_id,
                variants=variants,
                recommended_variant_id=recommended_variant_id,
                debug={"correlation_id": correlation_id} if context.tone == "debug" else None
            )
            
        except Exception as e:
            logger.error(f"Erro ao gerar criativo: {e}", exc_info=True)
            raise
    
    def generate_variants(
        self,
        creative_id: str,
        strategies: List[str],
        context: CreativeContext
    ) -> List[CreativeVariant]:
        """
        Gera variantes de um criativo usando estratégias específicas
        
        Args:
            creative_id: ID do criativo base
            strategies: Lista de estratégias a aplicar
            context: Contexto de geração
        
        Returns:
            Lista de variantes geradas
        """
        # Em MVP, buscar product_id do creative_id (futuro: DB)
        # Por enquanto, assumir que creative_id contém product_id
        product_id = creative_id.split("_")[0] if "_" in creative_id else creative_id
        
        product_data = self._get_product_data(product_id)
        
        return self._generate_variants(
            product_data=product_data,
            strategies=strategies,
            context=context
        )
    
    def _generate_variants(
        self,
        product_data: Dict[str, Any],
        strategies: List[str],
        context: CreativeContext,
        correlation_id: Optional[str] = None
    ) -> List[CreativeVariant]:
        """Gera variantes usando estratégias"""
        variants = []
        
        for strategy_name in strategies:
            if strategy_name not in self.strategies:
                logger.warning(f"Estratégia desconhecida: {strategy_name}")
                continue
            
            strategy = self.strategies[strategy_name]
            
            try:
                # Gerar brief
                brief = strategy.generate_brief(
                    product_data=product_data,
                    context=context
                )
                
                # Gerar textos
                texts = self.text_generator.generate(
                    brief=brief.__dict__,
                    context=context,
                    product_data=product_data
                )
                
                # Gerar discurso
                discourse = self.discourse_generator.generate(
                    brief=brief.__dict__,
                    context=context,
                    product_data=product_data
                )
                
                # Obter imagem
                image_url = self.image_generator.get_image_url(
                    product_data=product_data,
                    context=context
                )
                
                # Criar variante
                variant_id = str(uuid.uuid4())
                variant = CreativeVariant(
                    variant_id=variant_id,
                    strategy=strategy_name,
                    channel=context.channel,
                    image_url=image_url,
                    text_short=texts.get("text_short"),
                    text_medium=texts.get("text_medium"),
                    text_long=texts.get("text_long"),
                    discourse=discourse,
                    ctas=[brief.cta],
                )
                
                variants.append(variant)
                
                # Emitir evento
                emit_creative_event(
                    event_type=CreativeEventType.CREATIVE_VARIANT_GENERATED,
                    data={
                        "strategy": strategy_name,
                        "channel": context.channel,
                    },
                    product_id=str(product_data.get("id", "")),
                    variant_id=variant_id,
                    correlation_id=correlation_id
                )
                
            except Exception as e:
                logger.error(f"Erro ao gerar variante {strategy_name}: {e}", exc_info=True)
                continue
        
        return variants
    
    def adapt_creative(
        self,
        variant_id: str,
        channel: str,
        context: CreativeContext
    ) -> Dict[str, Any]:
        """
        Adapta variante para canal específico
        
        Args:
            variant_id: ID da variante
            channel: Canal de destino
            context: Contexto de adaptação
        
        Returns:
            Payload adaptado para o canal
        """
        # Em MVP, buscar variante do cache/DB (futuro: persistência)
        # Por enquanto, retornar erro se não houver variante
        logger.warning(f"Adaptação de variante {variant_id} - MVP: retornando formato genérico")
        
        from services.creative_engine_service.adapters.generic import GenericAdapter
        adapter = GenericAdapter()
        
        # Criar variante mock (futuro: buscar do DB)
        variant = CreativeVariant(
            variant_id=variant_id,
            strategy="unknown",
            channel=channel,
        )
        
        result = adapter.adapt(variant, context)
        
        emit_creative_event(
            event_type=CreativeEventType.CREATIVE_ADAPTED,
            data={
                "variant_id": variant_id,
                "channel": channel,
            },
            variant_id=variant_id
        )
        
        return result
    
    def register_performance(self, event: Dict[str, Any]) -> None:
        """
        Registra evento de performance
        
        Args:
            event: Evento de performance (VIEWED, RESPONDED, etc)
        """
        event_type_str = event.get("type")
        variant_id = event.get("variant_id")
        shopper_id = event.get("shopper_id")
        product_id = event.get("product_id")
        
        # Mapear tipo de evento
        event_type_map = {
            "VIEWED": CreativeEventType.CREATIVE_VIEWED,
            "RESPONDED": CreativeEventType.CREATIVE_RESPONDED,
            "INTERESTED": CreativeEventType.CREATIVE_INTERESTED,
            "ORDERED": CreativeEventType.CREATIVE_ORDERED,
            "CONVERTED": CreativeEventType.CREATIVE_CONVERTED,
            "IGNORED": CreativeEventType.CREATIVE_IGNORED,
        }
        
        event_type = event_type_map.get(event_type_str)
        if not event_type:
            logger.warning(f"Tipo de evento desconhecido: {event_type_str}")
            return
        
        emit_creative_event(
            event_type=event_type,
            data=event.get("data", {}),
            shopper_id=shopper_id,
            product_id=product_id,
            variant_id=variant_id,
            correlation_id=event.get("correlation_id")
        )
    
    def recommend_next(
        self,
        shopper_id: str,
        product_id: str,
        context: CreativeContext
    ) -> CreativeResponse:
        """
        Recomenda próximo criativo baseado em aprendizado
        
        Args:
            shopper_id: ID do shopper
            product_id: ID do produto
            context: Contexto atual
        
        Returns:
            CreativeResponse com recomendação otimizada
        """
        # Em MVP, usar mesma lógica de generate_creative
        # Futuro: usar histórico de performance para otimizar
        return self.generate_creative(
            product_id=product_id,
            shopper_id=shopper_id,
            context=context
        )
    
    def _get_product_data(self, product_id: str) -> Dict[str, Any]:
        """
        Busca dados do produto
        
        Args:
            product_id: ID do produto
        
        Returns:
            Dict com dados do produto
        """
        try:
            from app_sinapum.models import Produto
            produto = Produto.objects.get(id=product_id)
            
            return {
                "id": str(produto.id),
                "nome": produto.nome,
                "marca": produto.marca,
                "descricao": produto.descricao,
                "categoria": produto.categoria,
                "subcategoria": produto.subcategoria,
                "volume_ml": produto.volume_ml,
                "imagens": produto.imagens,
            }
        except ObjectDoesNotExist:
            logger.error(f"Produto não encontrado: {product_id}")
            raise ValueError(f"Produto {product_id} não encontrado")
        except Exception as e:
            logger.error(f"Erro ao buscar produto: {e}", exc_info=True)
            raise
