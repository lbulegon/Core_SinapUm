"""
Utilitários para o MCP Tool Registry
"""
import logging
import requests
from django.conf import settings

logger = logging.getLogger(__name__)


def resolve_prompt_from_ref(prompt_ref, config=None):
    """
    Resolve um prompt_ref do ToolVersion para o texto do prompt.
    
    Suporta múltiplas fontes de prompts (MCP completo):
    1. PostgreSQL (PromptTemplate): "nome", "sistema:nome", "sistema:tipo"
    2. URL externa: "http://..." ou "https://..."
    3. Inline no config: se config.get("prompt_inline") existir
    4. Arquivo local: "file://..." (futuro)
    
    Args:
        prompt_ref: String com a referência do prompt
        config: Dict opcional com configurações adicionais (ex: prompt_inline)
        
    Returns:
        str: Texto do prompt ou None se não encontrado
    """
    if not prompt_ref:
        # Tentar buscar prompt inline no config
        if config and config.get("prompt_inline"):
            logger.info("Usando prompt inline do config")
            return config["prompt_inline"]
        return None
    
    # 1. Verificar se é URL externa
    if prompt_ref.startswith("http://") or prompt_ref.startswith("https://"):
        try:
            logger.info(f"Buscando prompt de URL externa: {prompt_ref}")
            response = requests.get(prompt_ref, timeout=5)
            response.raise_for_status()
            prompt_text = response.text.strip()
            logger.info(f"Prompt carregado de URL: {len(prompt_text)} caracteres")
            return prompt_text
        except Exception as e:
            logger.error(f"Erro ao buscar prompt de URL '{prompt_ref}': {e}")
            return None
    
    # 2. Verificar se é prompt inline no config (prioridade sobre prompt_ref)
    if config and config.get("prompt_inline"):
        logger.info("Usando prompt inline do config (sobrescreve prompt_ref)")
        return config["prompt_inline"]
    
    # 3. Buscar no PostgreSQL (PromptTemplate)
    try:
        # Importar aqui para evitar dependência circular
        from app_sinapum.models import PromptTemplate, Sistema
        
        # Parse do formato
        if ':' in prompt_ref:
            # Formato: "sistema:nome" ou "sistema:tipo"
            sistema_codigo, ref = prompt_ref.split(':', 1)
            try:
                sistema = Sistema.objects.get(codigo=sistema_codigo, ativo=True)
            except Sistema.DoesNotExist:
                logger.warning(f"Sistema '{sistema_codigo}' não encontrado para prompt_ref '{prompt_ref}'")
                return None
            
            # Tentar buscar por nome primeiro
            prompt = PromptTemplate.objects.filter(
                sistema=sistema,
                nome=ref,
                ativo=True
            ).first()
            
            if prompt:
                return prompt.get_prompt_text_com_parametros()
            
            # Se não encontrou por nome, tentar como tipo_prompt
            prompt = PromptTemplate.get_prompt_ativo(ref, sistema=sistema)
            if prompt:
                return prompt.get_prompt_text_com_parametros()
            
            logger.warning(f"Prompt não encontrado para prompt_ref '{prompt_ref}'")
            return None
        else:
            # Formato simples: apenas nome (buscar no sistema padrão)
            sistema_codigo = getattr(settings, 'SISTEMA_CODIGO', 'evora')
            try:
                sistema = Sistema.objects.get(codigo=sistema_codigo, ativo=True)
            except Sistema.DoesNotExist:
                logger.warning(f"Sistema padrão '{sistema_codigo}' não encontrado para prompt_ref '{prompt_ref}'")
                return None
            
            prompt = PromptTemplate.objects.filter(
                sistema=sistema,
                nome=prompt_ref,
                ativo=True
            ).first()
            
            if prompt:
                return prompt.get_prompt_text_com_parametros()
            
            logger.warning(f"Prompt '{prompt_ref}' não encontrado no sistema '{sistema_codigo}'")
            return None
            
    except Exception as e:
        logger.error(f"Erro ao resolver prompt_ref '{prompt_ref}': {e}", exc_info=True)
        return None

