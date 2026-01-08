# ============================================================================
# ARQUITETURA NOVA - app_mcp.views
# ============================================================================
# Views para MCP Tools
# ============================================================================

import json
import logging
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

logger = logging.getLogger(__name__)


@csrf_exempt
@require_http_methods(["POST"])
def execute_tool(request, tool_name: str):
    """
    Executa uma tool MCP
    
    Endpoint: POST /mcp/tools/<tool_name>
    
    Body:
    {
        "shopper_id": "uuid",
        "args": {...}
    }
    
    Tools disponíveis:
    - customer.get_or_create
    - catalog.search
    - product.get
    - cart.get
    - cart.add
    - order.create
    - order.status
    """
    try:
        data = json.loads(request.body)
        shopper_id = data.get('shopper_id')
        args = data.get('args', {})
        
        if not shopper_id:
            return JsonResponse({'error': 'shopper_id é obrigatório'}, status=400)
        
        # Importar tools
        from .tools import (
            customer_get_or_create,
            catalog_search,
            product_get,
            cart_get,
            cart_add,
            order_create,
            order_status,
        )
        
        # Mapear tools
        tools = {
            'customer.get_or_create': lambda s, a: customer_get_or_create(s, a.get('phone', '')),
            'catalog.search': lambda s, a: catalog_search(s, a.get('query', ''), a.get('filters')),
            'product.get': lambda s, a: product_get(s, a.get('product_id', '')),
            'cart.get': lambda s, a: cart_get(s, a.get('customer_id', '')),
            'cart.add': lambda s, a: cart_add(s, a.get('customer_id', ''), a.get('product_id', ''), a.get('quantity', 1)),
            'order.create': lambda s, a: order_create(s, a.get('customer_id', ''), a.get('cart_id', ''), a.get('address', {}), a.get('payment_method', '')),
            'order.status': lambda s, a: order_status(s, a.get('order_id', '')),
        }
        
        if tool_name not in tools:
            return JsonResponse({'error': f'Tool {tool_name} não encontrada'}, status=404)
        
        # Executar tool
        result = tools[tool_name](shopper_id, args)
        return JsonResponse(result)
        
    except json.JSONDecodeError:
        return JsonResponse({'error': 'JSON inválido'}, status=400)
    except Exception as e:
        logger.error(f"Erro ao executar tool {tool_name}: {e}", exc_info=True)
        return JsonResponse({'error': str(e)}, status=500)

