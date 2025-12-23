"""
Normalização Semiótica - Normaliza estímulos para análise orbital
Baseado em teoria semiótica de Peirce
"""

from typing import Dict, Optional, List
import re


class SemioticNormalizer:
    """
    Normaliza estímulos (texto, imagem, marca, etc.) para análise semiótica
    """
    
    def __init__(self):
        self.semiotic_categories = {
            'icon': ['imagem', 'foto', 'visual', 'desenho', 'ilustração'],
            'index': ['causa', 'efeito', 'sinal', 'indicador', 'referência'],
            'symbol': ['palavra', 'texto', 'marca', 'nome', 'conceito']
        }
    
    def normalize(
        self, 
        stimulus: Dict,
        context: Optional[Dict] = None
    ) -> Dict:
        """
        Normaliza estímulo para análise semiótica
        
        Args:
            stimulus: Estímulo a normalizar
                - text: str (texto)
                - image_url: str (URL de imagem)
                - brand: str (marca)
                - type: str (tipo de estímulo)
            context: Contexto adicional
        
        Returns:
            Dict normalizado com campos semióticos
        """
        normalized = {
            'text': '',
            'semiotic_type': 'symbol',  # padrão
            'categories': [],
            'tokens': [],
            'metadata': {}
        }
        
        # Extrair texto
        if 'text' in stimulus:
            normalized['text'] = self._clean_text(stimulus['text'])
            normalized['tokens'] = self._tokenize(normalized['text'])
        
        # Determinar tipo semiótico
        if 'type' in stimulus:
            normalized['semiotic_type'] = self._determine_semiotic_type(
                stimulus['type'],
                normalized['text']
            )
        else:
            normalized['semiotic_type'] = self._infer_semiotic_type(stimulus)
        
        # Categorias semióticas
        normalized['categories'] = self._extract_categories(
            normalized['text'],
            normalized['semiotic_type']
        )
        
        # Metadados
        normalized['metadata'] = {
            'original_type': stimulus.get('type', 'unknown'),
            'has_image': 'image_url' in stimulus or 'image' in stimulus,
            'has_brand': 'brand' in stimulus,
            'length': len(normalized['text']),
            'token_count': len(normalized['tokens'])
        }
        
        # Adicionar contexto se disponível
        if context:
            normalized['metadata']['context'] = context
        
        return normalized
    
    def _clean_text(self, text: str) -> str:
        """Limpa e normaliza texto"""
        if not text:
            return ''
        
        # Converter para minúsculas
        text = text.lower()
        
        # Remover caracteres especiais excessivos
        text = re.sub(r'[^\w\s]', ' ', text)
        
        # Remover espaços múltiplos
        text = re.sub(r'\s+', ' ', text)
        
        return text.strip()
    
    def _tokenize(self, text: str) -> List[str]:
        """Tokeniza texto"""
        if not text:
            return []
        
        return text.split()
    
    def _determine_semiotic_type(self, type_str: str, text: str) -> str:
        """Determina tipo semiótico baseado no tipo declarado"""
        type_lower = type_str.lower()
        
        if any(word in type_lower for word in ['imagem', 'image', 'visual', 'foto']):
            return 'icon'
        elif any(word in type_lower for word in ['sinal', 'indicador', 'referência']):
            return 'index'
        else:
            return 'symbol'
    
    def _infer_semiotic_type(self, stimulus: Dict) -> str:
        """Infere tipo semiótico do estímulo"""
        if 'image_url' in stimulus or 'image' in stimulus:
            return 'icon'
        elif 'signal' in stimulus or 'indicator' in stimulus:
            return 'index'
        else:
            return 'symbol'
    
    def _extract_categories(self, text: str, semiotic_type: str) -> List[str]:
        """Extrai categorias semióticas do texto"""
        categories = []
        
        # Verificar palavras-chave por categoria
        for category, keywords in self.semiotic_categories.items():
            if any(keyword in text for keyword in keywords):
                categories.append(category)
        
        # Se não encontrou, usar tipo semiótico
        if not categories:
            categories.append(semiotic_type)
        
        return categories

