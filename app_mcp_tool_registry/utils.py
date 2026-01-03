"""
Utilitários para o MCP Tool Registry
"""
import logging
import requests
from django.conf import settings

logger = logging.getLogger(__name__)


def resolve_prompt_info(prompt_ref, config=None):
    """
    Resolve um prompt_ref e retorna informações completas do prompt.
    
    Returns:
        dict: {
            'text': str,  # Texto do prompt
            'nome': str,  # Nome do prompt
            'versao': str,  # Versão
            'fonte': str,  # 'PostgreSQL', 'URL', 'inline', 'fallback'
            'sistema': str,  # Sistema ou None
            'tipo_prompt': str,  # Tipo do prompt
            'parametros': dict,  # Parâmetros (temperature, max_tokens, etc.)
            'prompt_ref': str  # Referência original
        } ou None se não encontrado
    """
    prompt_info = {
        'text': None,
        'nome': None,
        'versao': None,
        'fonte': None,
        'sistema': None,
        'tipo_prompt': 'analise_imagem_produto',
        'parametros': {},
        'prompt_ref': prompt_ref
    }
    
    if not prompt_ref:
        # Tentar buscar prompt inline no config
        if config and config.get("prompt_inline"):
            prompt_info['text'] = config["prompt_inline"]
            prompt_info['nome'] = 'Inline (config)'
            prompt_info['versao'] = 'N/A'
            prompt_info['fonte'] = 'inline'
            prompt_info['sistema'] = None
            logger.info("Usando prompt inline do config")
            return prompt_info
        return None
    
    # 1. Verificar se é URL externa
    if prompt_ref.startswith("http://") or prompt_ref.startswith("https://"):
        try:
            logger.info(f"Buscando prompt de URL externa: {prompt_ref}")
            response = requests.get(prompt_ref, timeout=5)
            response.raise_for_status()
            prompt_text = response.text.strip()
            prompt_info['text'] = prompt_text
            prompt_info['nome'] = f'URL: {prompt_ref}'
            prompt_info['versao'] = 'N/A'
            prompt_info['fonte'] = 'URL'
            prompt_info['sistema'] = None
            logger.info(f"Prompt carregado de URL: {len(prompt_text)} caracteres")
            return prompt_info
        except Exception as e:
            logger.error(f"Erro ao buscar prompt de URL '{prompt_ref}': {e}")
            return None
    
    # 2. Verificar se é prompt inline no config (prioridade sobre prompt_ref)
    if config and config.get("prompt_inline"):
        prompt_info['text'] = config["prompt_inline"]
        prompt_info['nome'] = 'Inline (config)'
        prompt_info['versao'] = 'N/A'
        prompt_info['fonte'] = 'inline'
        prompt_info['sistema'] = None
        logger.info("Usando prompt inline do config (sobrescreve prompt_ref)")
        return prompt_info
    
    # 3. Buscar no PostgreSQL (PromptTemplate)
    try:
        from app_sinapum.models import PromptTemplate, Sistema
        
        prompt_template = None
        
        # Parse do formato
        if ':' in prompt_ref:
            sistema_codigo, ref = prompt_ref.split(':', 1)
            try:
                sistema = Sistema.objects.get(codigo=sistema_codigo, ativo=True)
                prompt_template = PromptTemplate.objects.filter(
                    sistema=sistema, nome=ref, ativo=True
                ).first()
                if not prompt_template:
                    prompt_template = PromptTemplate.get_prompt_ativo(ref, sistema=sistema)
            except Sistema.DoesNotExist:
                logger.warning(f"Sistema '{sistema_codigo}' não encontrado")
        else:
            # Buscar global primeiro
            prompt_template = PromptTemplate.objects.filter(
                sistema=None, nome=prompt_ref, ativo=True
            ).first()
            if not prompt_template:
                prompt_template = PromptTemplate.get_prompt_ativo(prompt_ref, sistema=None)
        
        if prompt_template:
            prompt_info['text'] = prompt_template.get_prompt_text_com_parametros()
            prompt_info['nome'] = prompt_template.nome
            prompt_info['versao'] = prompt_template.versao
            prompt_info['fonte'] = 'PostgreSQL'
            prompt_info['sistema'] = prompt_template.sistema.codigo if prompt_template.sistema else 'Global'
            prompt_info['tipo_prompt'] = prompt_template.tipo_prompt
            prompt_info['parametros'] = prompt_template.parametros if hasattr(prompt_template, 'parametros') and prompt_template.parametros else {}
            return prompt_info
        
        logger.warning(f"Prompt '{prompt_ref}' não encontrado")
        return None
        
    except Exception as e:
        logger.error(f"Erro ao resolver prompt_ref '{prompt_ref}': {e}", exc_info=True)
        return None


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
    prompt_info = resolve_prompt_info(prompt_ref, config)
    return prompt_info['text'] if prompt_info else None
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
            # Formato simples: apenas nome (buscar no sistema padrão ou global)
            sistema_codigo = getattr(settings, 'SISTEMA_CODIGO', 'evora')
            sistema = None
            
            try:
                sistema = Sistema.objects.get(codigo=sistema_codigo, ativo=True)
                logger.info(f"Buscando prompt '{prompt_ref}' no sistema '{sistema_codigo}'")
            except Sistema.DoesNotExist:
                logger.info(f"Sistema padrão '{sistema_codigo}' não encontrado, buscando prompt global")
            
            # Se tem sistema, tentar buscar nele primeiro
            if sistema:
                # Tentar buscar por nome primeiro
                prompt = PromptTemplate.objects.filter(
                    sistema=sistema,
                    nome=prompt_ref,
                    ativo=True
                ).first()
                
                if prompt:
                    logger.info(f"✅ Prompt encontrado por nome no sistema '{sistema_codigo}'")
                    return prompt.get_prompt_text_com_parametros()
                
                # Se não encontrou por nome, tentar como tipo_prompt
                prompt = PromptTemplate.get_prompt_ativo(prompt_ref, sistema=sistema)
                if prompt:
                    logger.info(f"✅ Prompt encontrado por tipo_prompt no sistema '{sistema_codigo}'")
                    return prompt.get_prompt_text_com_parametros()
            
            # Se não encontrou com sistema ou não tem sistema, tentar global (sem sistema)
            logger.info(f"Buscando prompt '{prompt_ref}' globalmente (sem sistema)")
            
            # Primeiro tentar buscar por nome (sem sistema)
            prompt = PromptTemplate.objects.filter(
                sistema=None,
                nome=prompt_ref,
                ativo=True
            ).first()
            
            if prompt:
                logger.info(f"✅ Prompt encontrado por nome globalmente")
                return prompt.get_prompt_text_com_parametros()
            
            # Se não encontrou por nome, tentar como tipo_prompt
            prompt = PromptTemplate.get_prompt_ativo(prompt_ref, sistema=None)
            if prompt:
                logger.info(f"✅ Prompt encontrado por tipo_prompt globalmente")
                return prompt.get_prompt_text_com_parametros()
            
            logger.warning(f"Prompt '{prompt_ref}' não encontrado (sistema '{sistema_codigo}' nem globalmente)")
            return None
            
    except Exception as e:
        logger.error(f"Erro ao resolver prompt_ref '{prompt_ref}': {e}", exc_info=True)
        return None

