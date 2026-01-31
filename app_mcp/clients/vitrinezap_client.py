# ============================================================================
# ARQUITETURA NOVA - app_mcp.clients.vitrinezap_client
# ============================================================================
# Cliente para API do VitrineZap/Évora
# ============================================================================

import requests
import logging
from typing import Dict, Any, Optional
from django.conf import settings

logger = logging.getLogger(__name__)


class VitrineZapClient:
    """
    Cliente para API do VitrineZap/Évora
    """
    
    def __init__(self, base_url: Optional[str] = None, token: Optional[str] = None):
        """
        Inicializa cliente VitrineZap
        
        Args:
            base_url: URL base do VitrineZap (default: VITRINEZAP_BASE_URL)
            token: Token de autenticação (default: INTERNAL_API_TOKEN)
        """
        self.base_url = base_url or getattr(settings, 'VITRINEZAP_BASE_URL', 'http://69.169.102.84:8000')
        self.token = token or getattr(settings, 'INTERNAL_API_TOKEN', '')
        self.timeout = 30
        
        # Headers
        self.headers = {
            'Content-Type': 'application/json',
        }
        if self.token:
            self.headers['Authorization'] = f'Bearer {self.token}'
    
    def _request(self, method: str, endpoint: str, data: Optional[Dict] = None, extra_headers: Optional[Dict] = None) -> Dict[str, Any]:
        path = endpoint if endpoint.startswith('/') else f'/{endpoint}'
        url = f"{self.base_url.rstrip('/')}{path}"
        headers = {**self.headers, **(extra_headers or {})}
        try:
            response = requests.request(
                method=method,
                url=url,
                headers=headers,
                json=data if method in ('POST', 'PUT', 'PATCH') else None,
                timeout=self.timeout
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Erro ao fazer requisição para VitrineZap {url}: {e}")
            return {'success': False, 'error': str(e)}
    
    def get_customer(self, shopper_id: str, phone: str) -> Dict[str, Any]:
        """
        Obtém ou cria cliente
        
        Args:
            shopper_id: ID do Shopper
            phone: Telefone do cliente
        
        Returns:
            {
                'success': bool,
                'customer_id': str,
                'customer': {...}
            }
        """
        # TODO: Implementar endpoint no VitrineZap
        # Por enquanto, retornar stub
        return {
            'success': True,
            'customer_id': f'customer_{phone}',
            'customer': {
                'id': f'customer_{phone}',
                'phone': phone,
            }
        }
    
    def search_catalog(self, shopper_id: str, query: str, filters: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Busca no catálogo do shopper.
        shopper_id pode ser subdomínio do catálogo (ex: 'minhaloja') ou UUID do PersonalShopper.
        Evora: GET /catalogo/<subdominio>/api/
        """
        try:
            subdominio = str(shopper_id).lower().replace(' ', '-')[:64]
            endpoint = f"/catalogo/{subdominio}/api/"
            resp = self._request('GET', endpoint)
            if not isinstance(resp, dict):
                return {'success': False, 'products': [], 'error': 'Resposta inválida'}
            if 'error' in resp:
                return {'success': False, 'products': [], 'error': resp.get('error', 'Catálogo não encontrado')}
            produtos = resp.get('produtos', [])
            if query and query.strip():
                q = query.strip().lower()
                produtos = [
                    p for p in produtos
                    if q in (p.get('nome', '') or '').lower()
                    or q in (p.get('descricao', '') or '').lower()
                    or q in (p.get('categoria', '') or '').lower()
                    or q in (p.get('marca', '') or '').lower()
                ]
            if filters:
                cat = (filters.get('categoria') or '').strip().lower()
                if cat:
                    produtos = [p for p in produtos if (p.get('categoria') or '').lower() == cat]
            return {'success': True, 'products': produtos, 'total': len(produtos)}
        except Exception as e:
            logger.warning(f"Erro ao buscar catálogo shopper={shopper_id}: {e}")
            return {'success': False, 'products': [], 'error': str(e)}
    
    def get_product(self, shopper_id: str, product_id: str) -> Dict[str, Any]:
        """
        Obtém produto do catálogo. Busca no catálogo e filtra por id.
        """
        catalog = self.search_catalog(shopper_id, '')
        if not catalog.get('success'):
            return {'success': False, 'product': None, 'error': catalog.get('error')}
        for p in catalog.get('products', []):
            if str(p.get('id')) == str(product_id):
                return {'success': True, 'product': p}
        return {'success': False, 'product': None, 'error': 'Produto não encontrado'}
    
    def get_cart(self, shopper_id: str, customer_id: str) -> Dict[str, Any]:
        """
        Obtém carrinho. Evora: GET /api/client/cart/info/ (requer auth de cliente).
        """
        extra = {'X-Customer-Id': str(customer_id)} if customer_id else {}
        resp = self._request('GET', '/api/client/cart/info/', extra_headers=extra)
        if resp.get('total_itens') is not None:
            return {'success': True, 'cart': resp}
        return {'success': False, 'cart': {}, 'error': resp.get('error', 'Carrinho não disponível')}
    
    def add_to_cart(self, shopper_id: str, customer_id: str, product_id: str, quantity: int = 1) -> Dict[str, Any]:
        """
        Adiciona produto ao carrinho.
        Evora: POST /api/client/cart/add/ (requer auth de cliente).
        Quando Evora expuser API headless com X-Internal-Token + customer_id, esta chamada funcionará.
        """
        endpoint = '/api/client/cart/add/'
        data = {'product_id': product_id, 'quantity': quantity}
        extra = {'X-Customer-Id': str(customer_id)} if customer_id else {}
        resp = self._request('POST', endpoint, data, extra_headers=extra)
        if resp.get('success'):
            return {'success': True, 'cart': resp.get('cart', resp)}
        return {'success': False, 'cart': {}, 'error': resp.get('error', 'Falha ao adicionar')}
    
    def create_order(self, shopper_id: str, customer_id: str, cart_id: str, address: Dict, payment_method: str) -> Dict[str, Any]:
        """
        Cria pedido. Evora: POST /api/client/cart/checkout/
        """
        extra = {'X-Customer-Id': str(customer_id)} if customer_id else {}
        data = {
            'cart_id': cart_id,
            'address': address,
            'payment_method': payment_method or 'pix',
        }
        resp = self._request('POST', '/api/client/cart/checkout/', data, extra_headers=extra)
        if resp.get('success') or resp.get('order_id'):
            return {'success': True, 'order_id': resp.get('order_id', ''), 'order': resp}
        return {'success': False, 'order_id': '', 'order': {}, 'error': resp.get('error', 'Falha ao criar pedido')}
    
    def get_order_status(self, shopper_id: str, order_id: str) -> Dict[str, Any]:
        """
        Obtém status do pedido
        
        Args:
            shopper_id: ID do Shopper
            order_id: ID do pedido
        
        Returns:
            {
                'success': bool,
                'status': str,
                'order': {...}
            }
        """
        # TODO: Implementar endpoint no VitrineZap
        return {
            'success': True,
            'status': 'pending',
            'order': {}
        }

