"""Serviço de recomendação de produtos"""
from typing import List
from app.schemas.recommendation import RecommendationRequest, RecommendationResponse, RecommendedProduct, ProductHighlight
from app.schemas.intent import IntentType
from app.schemas.catalog import ProductSearchResult
from app.storage.catalog import CatalogStorage
from app.services.intent_service import IntentService


class RecommendationService:
    """Recomenda produtos baseado em intenção"""
    
    def __init__(self, catalog_storage: CatalogStorage):
        self.catalog_storage = catalog_storage
    
    def recommend(self, request: RecommendationRequest) -> RecommendationResponse:
        """Recomenda produtos"""
        intent = request.intent_payload.intent
        filtros = request.filtros
        
        # Buscar produtos no catálogo
        query = self._build_search_query(request.intent_payload)
        candidates = self.catalog_storage.search_products(
            query=query,
            estabelecimento_id=filtros.estabelecimento_id,
            limit=filtros.max_results * 2,  # Buscar mais para filtrar depois
            categoria=filtros.categoria
        )
        
        # Filtrar por faixa de preço se especificado
        if filtros.faixa_preco:
            candidates = self._filter_by_price_range(candidates, filtros.faixa_preco)
        
        # Ordenar e calcular scores
        recommended = []
        for candidate in candidates[:filtros.max_results]:
            # Converter ProductSearchResult para dict para compatibilidade com métodos auxiliares
            candidate_dict = {
                "product_id": candidate.product_id,
                "titulo": candidate.titulo,
                "descricao": candidate.descricao,
                "preco": candidate.preco,
                "categoria": candidate.categoria,
                "score": candidate.score
            }
            
            score = self._calculate_recommendation_score(candidate_dict, request.intent_payload)
            reason = self._generate_reason(candidate_dict, intent)
            highlights = self._generate_highlights(candidate_dict, request.intent_payload)
            
            recommended.append(RecommendedProduct(
                product_id=candidate.product_id,
                score=score,
                reason=reason,
                highlights=highlights
            ))
        
        # Ordenar por score
        recommended.sort(key=lambda x: x.score, reverse=True)
        
        return RecommendationResponse(
            products=recommended,
            intent=intent,
            total_candidates=len(candidates)
        )
    
    def _build_search_query(self, intent_payload) -> str:
        """Constrói query de busca baseado na intenção"""
        # Se há entidades extraídas, usar elas
        entities = intent_payload.extracted_entities
        
        query_parts = []
        if entities and entities.categoria:
            query_parts.append(entities.categoria)
        if entities and entities.produto:
            query_parts.append(entities.produto)
        
        # Se não há entidades, usar palavras da mensagem original
        # (assumindo que a mensagem está disponível no contexto)
        if not query_parts:
            query_parts.append("*")  # Busca ampla
        
        return " ".join(query_parts)
    
    def _filter_by_price_range(self, candidates: List[ProductSearchResult], faixa: str) -> List[ProductSearchResult]:
        """Filtra produtos por faixa de preço"""
        if not candidates:
            return candidates
        
        if faixa == "barato":
            # Ordenar por preço crescente e pegar os mais baratos
            sorted_candidates = sorted(candidates, key=lambda x: x.preco or 0)
            return sorted_candidates[:len(candidates) // 2]
        elif faixa == "caro":
            # Ordenar por preço decrescente
            sorted_candidates = sorted(candidates, key=lambda x: x.preco or 0, reverse=True)
            return sorted_candidates[:len(candidates) // 2]
        # "medio" retorna todos
        return candidates
    
    def _calculate_recommendation_score(self, product: dict, intent_payload) -> float:
        """Calcula score de recomendação"""
        base_score = product.get("score", 0.5)  # Score da busca
        
        # Boost baseado na intenção
        intent = intent_payload.intent
        if intent == IntentType.BUY_NOW:
            # Boost para produtos mais populares (assumindo que score indica popularidade)
            base_score *= 1.2
        elif intent == IntentType.PRICE_CHECK:
            # Manter score neutro
            pass
        elif intent == IntentType.COMPARE:
            # Boost para produtos com boa descrição
            descricao = product.get("descricao", "")
            if descricao and len(descricao) > 50:
                base_score *= 1.1
        
        return min(1.0, base_score)
    
    def _generate_reason(self, product: dict, intent: IntentType) -> str:
        """Gera motivo da recomendação"""
        titulo = product.get("titulo", "Produto")
        reasons = {
            IntentType.BUY_NOW: f"Produto '{titulo}' disponível",
            IntentType.COMPARE: f"Produto '{titulo}' para comparar",
            IntentType.PRICE_CHECK: f"Preço de '{titulo}'",
            IntentType.AVAILABILITY: f"'{titulo}' disponível no catálogo",
            IntentType.JUST_BROWSING: f"'{titulo}' - pode interessar",
        }
        return reasons.get(intent, f"Produto '{titulo}' recomendado")
    
    def _generate_highlights(self, product: dict, intent_payload) -> List[ProductHighlight]:
        """Gera highlights do produto"""
        highlights = []
        
        preco = product.get("preco")
        if preco:
            highlights.append(ProductHighlight(
                field="preco",
                value=f"R$ {preco:.2f}",
                match_reason="Preço disponível"
            ))
        
        categoria = product.get("categoria")
        if categoria:
            highlights.append(ProductHighlight(
                field="categoria",
                value=categoria,
                match_reason="Categoria do produto"
            ))
        
        return highlights

