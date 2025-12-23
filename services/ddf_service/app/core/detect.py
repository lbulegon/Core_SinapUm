"""
Módulo de Detecção - Classifica tarefas em categorias de IA
Baseado na classificação completa do PDF
"""

import re
from typing import Dict, List, Optional


class TaskDetector:
    """Detecta categoria e intenção de uma tarefa"""
    
    # Mapeamento de palavras-chave para categorias
    KEYWORDS = {
        'ideias': [
            'ideia', 'ideias', 'brainstorm', 'criar ideia', 'sugestão', 'sugestões',
            'pensar', 'planejar', 'estratégia', 'conceito', 'conceitos'
        ],
        'chatbot': [
            'chat', 'conversar', 'assistente', 'bot', 'atendimento', 'suporte',
            'pergunta', 'responder', 'dialogo', 'conversa'
        ],
        'ui_ux': [
            'interface', 'ui', 'ux', 'design interface', 'layout', 'telas',
            'wireframe', 'prototipo', 'mockup', 'user experience'
        ],
        'apresentacao': [
            'apresentação', 'slides', 'powerpoint', 'pitch', 'deck',
            'demonstração', 'exposição', 'mostrar'
        ],
        'website': [
            'site', 'website', 'página web', 'landing page', 'homepage',
            'criar site', 'fazer site', 'desenvolver site'
        ],
        'marketing': [
            'marketing', 'publicidade', 'anúncio', 'campanha', 'copy',
            'texto publicitário', 'ad copy', 'propaganda'
        ],
        'imagem': [
            'imagem', 'foto', 'fotografia', 'desenho', 'ilustração', 'arte',
            'gerar imagem', 'criar imagem', 'imagem ai', 'picture', 'image'
        ],
        'automacao': [
            'automação', 'automatizar', 'workflow', 'zapier', 'make',
            'integração', 'automatizar tarefa', 'rotina'
        ],
        'escrita': [
            'escrever', 'texto', 'artigo', 'redação', 'conteúdo', 'copywriting',
            'blog', 'post', 'descrição', 'criar texto'
        ],
        'voz_para_texto': [
            'transcrever', 'transcrição', 'áudio para texto', 'voz para texto',
            'speech to text', 'legendar', 'legenda'
        ],
        'texto_para_voz': [
            'texto para voz', 'voz', 'narração', 'audio', 'tts',
            'text to speech', 'falar', 'narrador'
        ],
        'video': [
            'vídeo', 'video', 'filme', 'criar vídeo', 'gerar vídeo',
            'animações', 'clipe', 'produção'
        ],
        'blogging': [
            'blog', 'postagem', 'artigo blog', 'conteúdo blog',
            'publicar', 'postar'
        ],
        'reunioes': [
            'reunião', 'meeting', 'transcrição reunião', 'ata',
            'resumo reunião', 'gravação'
        ],
        'design': [
            'design', 'gráfico', 'logo', 'banner', 'cartaz', 'flyer',
            'criar design', 'fazer design'
        ],
        'ai_detector': [
            'detectar ia', 'verificar autenticidade', 'detector',
            'plágio', 'originalidade', 'verificar texto'
        ]
    }
    
    def detect(self, text: str, context: Optional[Dict] = None) -> Dict:
        """
        Detecta categoria e intenção de uma tarefa
        
        Args:
            text: Texto da tarefa
            context: Contexto adicional (projeto, usuário, etc.)
        
        Returns:
            Dict com categoria, intenção, confiança e metadados
        """
        text_lower = text.lower()
        
        # Buscar categoria por palavras-chave
        category_scores = {}
        for category, keywords in self.KEYWORDS.items():
            score = sum(1 for keyword in keywords if keyword in text_lower)
            if score > 0:
                category_scores[category] = score
        
        # Determinar categoria principal
        if category_scores:
            category = max(category_scores, key=category_scores.get)
            confidence = min(category_scores[category] / len(self.KEYWORDS[category]), 1.0)
        else:
            category = 'ideias'  # Fallback padrão
            confidence = 0.3
        
        # Detectar intenção
        intent = self._detect_intent(text_lower)
        
        # Detectar formato (se aplicável)
        format_type = self._detect_format(text_lower, category)
        
        # Detectar urgência
        urgency = self._detect_urgency(text_lower)
        
        return {
            'category': category,
            'intent': intent,
            'confidence': confidence,
            'format': format_type,
            'urgency': urgency,
            'original_text': text,
            'context': context or {}
        }
    
    def _detect_intent(self, text: str) -> str:
        """Detecta a intenção da tarefa"""
        if any(word in text for word in ['gerar', 'criar', 'fazer', 'produzir']):
            return 'gerar'
        elif any(word in text for word in ['editar', 'modificar', 'alterar', 'ajustar']):
            return 'editar'
        elif any(word in text for word in ['resumir', 'resumo', 'sumarizar']):
            return 'resumir'
        elif any(word in text for word in ['analisar', 'análise', 'verificar']):
            return 'analisar'
        elif any(word in text for word in ['traduzir', 'tradução']):
            return 'traduzir'
        else:
            return 'gerar'  # Padrão
    
    def _detect_format(self, text: str, category: str) -> Optional[str]:
        """Detecta formato desejado"""
        formats_map = {
            'imagem': ['png', 'jpg', 'jpeg', 'svg', 'webp'],
            'video': ['mp4', 'mov', 'avi'],
            'escrita': ['txt', 'md', 'docx', 'pdf'],
            'apresentacao': ['pptx', 'pdf', 'html']
        }
        
        if category in formats_map:
            for fmt in formats_map[category]:
                if fmt in text:
                    return fmt
        
        return None
    
    def _detect_urgency(self, text: str) -> str:
        """Detecta urgência da tarefa"""
        urgent_keywords = ['urgente', 'rápido', 'agora', 'imediato', 'asap']
        if any(keyword in text for keyword in urgent_keywords):
            return 'alta'
        return 'normal'


def detect_task(text: str, context: Optional[Dict] = None) -> Dict:
    """
    Função helper para detectar tarefa
    """
    detector = TaskDetector()
    return detector.detect(text, context)

