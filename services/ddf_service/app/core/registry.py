"""
Registry - Mantém registro de todos os providers de IA disponíveis
"""

import yaml
from typing import Dict, List
from pathlib import Path


class ProviderRegistry:
    """Registry centralizado de providers de IA"""
    
    def __init__(self):
        self.providers = self._load_providers()
        self._provider_metadata = self._init_metadata()
    
    def _load_providers(self) -> Dict:
        """Carrega providers do arquivo de configuração"""
        config_path = Path(__file__).parent.parent.parent / 'config' / 'providers.yaml'
        with open(config_path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    
    def _init_metadata(self) -> Dict:
        """Inicializa metadados dos providers"""
        return {
            # Ideias
            'chatgpt': {'name': 'ChatGPT', 'type': 'llm', 'cost': 'medium'},
            'gemini': {'name': 'Google Gemini', 'type': 'llm', 'cost': 'medium'},
            'claude': {'name': 'Claude AI', 'type': 'llm', 'cost': 'medium'},
            'perplexity': {'name': 'Perplexity', 'type': 'search_llm', 'cost': 'low'},
            'copilot': {'name': 'GitHub Copilot', 'type': 'code', 'cost': 'medium'},
            
            # Chatbot
            'monica': {'name': 'Monica', 'type': 'chatbot', 'cost': 'low'},
            'grok': {'name': 'Grok', 'type': 'chatbot', 'cost': 'medium'},
            'poe': {'name': 'Poe', 'type': 'chatbot', 'cost': 'low'},
            
            # UI/UX
            'galileo_ai': {'name': 'Galileo AI', 'type': 'ui_generator', 'cost': 'medium'},
            'khroma': {'name': 'Khroma', 'type': 'color', 'cost': 'free'},
            'uizard': {'name': 'Uizard', 'type': 'ui_generator', 'cost': 'medium'},
            'visily': {'name': 'Visily', 'type': 'ui_generator', 'cost': 'medium'},
            'visualeyes': {'name': 'VisualEyes', 'type': 'ui_analyzer', 'cost': 'medium'},
            
            # Apresentação
            'gamma': {'name': 'Gamma', 'type': 'presentation', 'cost': 'medium'},
            'tome': {'name': 'Tome', 'type': 'presentation', 'cost': 'medium'},
            'beautiful_ai': {'name': 'Beautiful.ai', 'type': 'presentation', 'cost': 'medium'},
            'slidebean': {'name': 'Slidebean', 'type': 'presentation', 'cost': 'medium'},
            'pitch': {'name': 'Pitch', 'type': 'presentation', 'cost': 'medium'},
            
            # Website
            'dora': {'name': 'Dora', 'type': 'website_builder', 'cost': 'medium'},
            'durable': {'name': 'Durable', 'type': 'website_builder', 'cost': 'medium'},
            'wegic': {'name': 'Wegic', 'type': 'website_builder', 'cost': 'medium'},
            'framer': {'name': 'Framer', 'type': 'website_builder', 'cost': 'high'},
            '10web': {'name': '10Web', 'type': 'website_builder', 'cost': 'medium'},
            
            # Marketing
            'adcopy': {'name': 'AdCopy', 'type': 'marketing', 'cost': 'medium'},
            'predis_ai': {'name': 'Predis AI', 'type': 'marketing', 'cost': 'medium'},
            'howler_ai': {'name': 'Howler AI', 'type': 'marketing', 'cost': 'medium'},
            'bardeen_ai': {'name': 'Bardeen AI', 'type': 'automation', 'cost': 'medium'},
            'adcreative': {'name': 'AdCreative', 'type': 'marketing', 'cost': 'medium'},
            
            # Imagem
            'midjourney': {'name': 'Midjourney', 'type': 'image_gen', 'cost': 'high'},
            'nano_banana': {'name': 'NANO BANANA', 'type': 'image_gen', 'cost': 'medium'},
            'stable_diffusion': {'name': 'Stable Diffusion', 'type': 'image_gen', 'cost': 'low'},
            'leonardo_ai': {'name': 'Leonardo AI', 'type': 'image_gen', 'cost': 'medium'},
            'adobe_firefly': {'name': 'Adobe Firefly', 'type': 'image_gen', 'cost': 'high'},
            
            # Automação
            'zapier': {'name': 'Zapier', 'type': 'automation', 'cost': 'high'},
            'make': {'name': 'Make', 'type': 'automation', 'cost': 'medium'},
            'phrasee': {'name': 'Phrasee', 'type': 'marketing_automation', 'cost': 'high'},
            'outreach': {'name': 'Outreach', 'type': 'sales_automation', 'cost': 'high'},
            'clickup': {'name': 'ClickUp', 'type': 'project_management', 'cost': 'medium'},
            
            # Escrita
            'jasper': {'name': 'Jasper', 'type': 'writing', 'cost': 'high'},
            'rytr': {'name': 'Rytr', 'type': 'writing', 'cost': 'low'},
            'textblaze': {'name': 'TextBlaze', 'type': 'writing', 'cost': 'low'},
            'sudowrite': {'name': 'Sudowrite', 'type': 'creative_writing', 'cost': 'medium'},
            'copy_ai': {'name': 'Copy.ai', 'type': 'writing', 'cost': 'medium'},
            'writer': {'name': 'Writer', 'type': 'writing', 'cost': 'medium'},
            
            # Voz para Texto
            'fluently_ai': {'name': 'Fluently AI', 'type': 'transcription', 'cost': 'medium'},
            'descript': {'name': 'Descript', 'type': 'transcription', 'cost': 'medium'},
            'rev_ai': {'name': 'Rev AI', 'type': 'transcription', 'cost': 'medium'},
            'clipto': {'name': 'Clipto', 'type': 'transcription', 'cost': 'low'},
            'textcortex': {'name': 'TextCortex', 'type': 'transcription', 'cost': 'medium'},
            
            # Texto para Voz
            'elevenlabs': {'name': 'ElevenLabs', 'type': 'tts', 'cost': 'medium'},
            'murf_ai': {'name': 'Murf AI', 'type': 'tts', 'cost': 'medium'},
            'speechify': {'name': 'Speechify', 'type': 'tts', 'cost': 'low'},
            'deepgram': {'name': 'Deepgram', 'type': 'tts', 'cost': 'medium'},
            'lovo': {'name': 'Lovo', 'type': 'tts', 'cost': 'medium'},
            
            # Vídeo
            'sora': {'name': 'Sora', 'type': 'video_gen', 'cost': 'high'},
            'pika': {'name': 'Pika', 'type': 'video_gen', 'cost': 'medium'},
            'runway': {'name': 'Runway', 'type': 'video_gen', 'cost': 'high'},
            'luma': {'name': 'Luma', 'type': 'video_gen', 'cost': 'medium'},
            'kling': {'name': 'Kling', 'type': 'video_gen', 'cost': 'medium'},
            
            # Reuniões
            'tldv': {'name': 'TLDV', 'type': 'meeting', 'cost': 'medium'},
            'krisp': {'name': 'Krisp', 'type': 'meeting', 'cost': 'low'},
            'otter': {'name': 'Otter', 'type': 'meeting', 'cost': 'medium'},
            'avoma': {'name': 'Avoma', 'type': 'meeting', 'cost': 'high'},
            'fireflies': {'name': 'Fireflies', 'type': 'meeting', 'cost': 'medium'},
            
            # Design
            'canva': {'name': 'Canva', 'type': 'design', 'cost': 'low'},
            'figma_ai': {'name': 'Figma (with AI)', 'type': 'design', 'cost': 'medium'},
            'looka': {'name': 'Looka', 'type': 'logo', 'cost': 'medium'},
            'clipdrop': {'name': 'Clipdrop', 'type': 'image_edit', 'cost': 'low'},
            'autodraw': {'name': 'Autodraw', 'type': 'drawing', 'cost': 'free'},
            
            # AI Detector
            'gptzero': {'name': 'GPTZero', 'type': 'detector', 'cost': 'low'},
            'originality_ai': {'name': 'Originality.ai', 'type': 'detector', 'cost': 'medium'},
            'turnitin': {'name': 'Turnitin', 'type': 'detector', 'cost': 'high'},
            'copyleaks': {'name': 'Copyleaks', 'type': 'detector', 'cost': 'medium'},
            'zerogpt': {'name': 'ZeroGPT', 'type': 'detector', 'cost': 'low'},
        }
    
    def get_providers_by_category(self, category: str) -> List[str]:
        """Retorna lista de providers para uma categoria"""
        return self.providers.get(category, [])
    
    def get_provider_metadata(self, provider: str) -> Dict:
        """Retorna metadados de um provider"""
        return self._provider_metadata.get(provider, {})
    
    def get_all_categories(self) -> List[str]:
        """Retorna todas as categorias disponíveis"""
        return list(self.providers.keys())
    
    def is_provider_available(self, category: str, provider: str) -> bool:
        """Verifica se um provider está disponível para uma categoria"""
        return provider in self.get_providers_by_category(category)


# Instância global do registry
REGISTRY = ProviderRegistry()

