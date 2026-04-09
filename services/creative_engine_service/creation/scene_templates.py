"""
SceneTemplateLibrary - Biblioteca de templates de cena (documento Kwai/Tamo)
"""
from typing import Dict, Any, List


# Templates conforme documento CREATIVE_ENGINE_ANALYSIS
TEMPLATES = {
    'fashion_accessories': [
        {
            'id': 'european_cafe',
            'name': 'Café Europeu Elegante',
            'description': 'Cena urbana sofisticada em café europeu',
            'model_type': 'elegant_woman',
            'background': 'outdoor cafe, european street, blurred background',
            'lighting': 'natural daylight, soft shadows',
            'mood': 'sophisticated, casual elegance',
            'camera_settings': 'shallow depth of field, 50mm lens',
            'composition': 'rule of thirds, model in motion',
            'color_palette': 'neutral tones, warm lighting',
            'suitable_for': ['bags', 'accessories', 'jewelry', 'sunglasses'],
        },
        {
            'id': 'minimal_studio',
            'name': 'Estúdio Minimalista',
            'description': 'Fundo limpo e profissional',
            'background': 'pure white, no distractions',
            'lighting': 'studio lighting, even illumination',
            'mood': 'clean, professional, e-commerce ready',
            'suitable_for': ['all products'],
        },
        {
            'id': 'urban_street',
            'name': 'Rua Urbana Moderna',
            'description': 'Ambiente urbano contemporâneo',
            'model_type': 'fashionable_person',
            'background': 'modern city street, architectural elements',
            'lighting': 'golden hour, natural light',
            'mood': 'trendy, contemporary, street style',
            'suitable_for': ['fashion', 'accessories', 'lifestyle'],
        },
        {
            'id': 'luxury_interior',
            'name': 'Interior Luxuoso',
            'description': 'Ambiente interno elegante',
            'model_type': 'sophisticated_model',
            'background': 'luxury hotel lobby, marble, elegant furniture',
            'lighting': 'ambient luxury lighting, warm tones',
            'mood': 'premium, exclusive, high-end',
            'suitable_for': ['premium products', 'luxury accessories'],
        },
    ],
    'geral': [
        {
            'id': 'minimal_studio',
            'name': 'Estúdio Minimalista',
            'description': 'Fundo limpo e profissional',
            'background': 'pure white, no distractions',
            'lighting': 'studio lighting, even illumination',
            'mood': 'clean, professional, e-commerce ready',
            'suitable_for': ['all products'],
        },
    ],
}


class SceneTemplateLibrary:
    """Biblioteca de templates de cena para geração de criativos"""

    def get_recommended(self, product_analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Retorna templates recomendados baseado na análise do produto.

        Args:
            product_analysis: Resultado do ImageAnalyzer.analyze()

        Returns:
            Lista de templates recomendados
        """
        category = product_analysis.get('product_category', 'geral')
        style = product_analysis.get('style', 'casual')
        price_range = product_analysis.get('price_range_suggested', 'médio')

        # Buscar templates da categoria
        templates = TEMPLATES.get(category, TEMPLATES.get('geral', []))
        if not templates:
            templates = TEMPLATES['geral']

        # Filtrar por suitable_for se product_type estiver mapeado
        product_type = product_analysis.get('product_type', '').lower()
        recommended = []
        for t in templates:
            suitable = t.get('suitable_for', ['all products'])
            if 'all products' in suitable or product_type in [s.lower() for s in suitable]:
                recommended.append(t)

        return recommended[:4] if recommended else templates[:2]

    def get_clean_product_template(self) -> Dict[str, Any]:
        """Template para foto de produto clean (e-commerce)"""
        return {
            'id': 'clean_product',
            'name': 'Produto Clean',
            'description': 'Fundo branco profissional',
            'background': 'pure white RGB 255,255,255',
            'lighting': 'studio lighting, even illumination',
            'mood': 'clean, professional, e-commerce ready',
        }
