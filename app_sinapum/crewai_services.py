"""
Serviços CrewAI para orquestração de agentes no VitrineZap
Integração com OpenMind AI para análise de produtos

O CrewAI usa o OpenMind.org como backend LLM, que oferece acesso a múltiplos
modelos (OpenAI, Anthropic, Gemini, etc.) através de uma API unificada.
"""
import logging
import requests
from typing import Dict, Any, List, Optional
from django.conf import settings

logger = logging.getLogger(__name__)

try:
    from crewai import Agent, Task, Crew, Process
    from crewai.tools import tool
    from langchain_openai import ChatOpenAI
    CREWAI_AVAILABLE = True
except ImportError:
    CREWAI_AVAILABLE = False
    logger.warning("CrewAI não está instalado. Execute: pip install crewai langchain-openai")

# Configurar LLM usando OpenMind.org
def get_openmind_llm(temperature: float = 0.7, model: str = None):
    """
    Cria um LLM configurado para usar OpenMind.org como backend.
    
    OpenMind.org oferece acesso a múltiplos LLMs (OpenAI, Anthropic, Gemini, etc.)
    através de uma API unificada.
    """
    if not CREWAI_AVAILABLE:
        return None
    
    # Usar a mesma chave do OpenMind já configurada
    api_key = getattr(settings, 'OPENMIND_AI_KEY', None) or getattr(settings, 'OPENMIND_ORG_API_KEY', '')
    
    # URL base do OpenMind.org para LLMs
    # OpenMind.org oferece endpoints compatíveis com OpenAI para múltiplos modelos
    base_url = getattr(settings, 'OPENMIND_ORG_BASE_URL', '')
    
    # Modelo padrão (pode ser gpt-4o, claude-3-opus, gemini-pro, etc.)
    model_name = model or getattr(settings, 'OPENMIND_ORG_MODEL', 'gpt-4o')
    
    if not api_key:
        logger.warning("OPENMIND_AI_KEY não configurada. Usando configuração padrão.")
        # Fallback para OpenAI direto se OpenMind key não estiver disponível
        api_key = getattr(settings, 'OPENAI_API_KEY', '')
        base_url = None  # Usar OpenAI direto
    
    try:
        # Criar LLM usando LangChain com OpenMind.org como backend
        llm = ChatOpenAI(
            model=model_name,
            temperature=temperature,
            api_key=api_key,
            base_url=base_url if base_url else None,  # Se None, usa OpenAI direto
        )
        logger.info(f"LLM configurado: {model_name} via OpenMind.org")
        return llm
    except Exception as e:
        logger.error(f"Erro ao configurar LLM: {str(e)}")
        return None


# Configurações
OPENMIND_AI_URL = getattr(settings, 'OPENMIND_AI_URL', 'http://127.0.0.1:8000')
OPENMIND_AI_KEY = getattr(settings, 'OPENMIND_AI_KEY', None)


# ============================================================================
# FERRAMENTAS (TOOLS) PARA OS AGENTES
# ============================================================================

@tool("Analisar imagem de produto com OpenMind")
def analisar_imagem_openmind(image_path: str) -> Dict[str, Any]:
    """
    Analisa uma imagem de produto usando o servidor OpenMind AI.
    
    Args:
        image_path: Caminho local da imagem ou dados da imagem
    
    Returns:
        dict: Dados extraídos do produto no formato modelo.json
    """
    if not CREWAI_AVAILABLE:
        return {"error": "CrewAI não está disponível"}
    
    try:
        url = f"{OPENMIND_AI_URL}/api/v1/analyze-product-image"
        
        headers = {}
        if OPENMIND_AI_KEY:
            headers['Authorization'] = f'Bearer {OPENMIND_AI_KEY}'
        
        # Abrir e enviar imagem
        with open(image_path, 'rb') as img_file:
            files = {'image': img_file}
            response = requests.post(url, files=files, headers=headers, timeout=60)
        
        if response.status_code == 200:
            result = response.json()
            if result.get('success') and result.get('data'):
                return result['data']
        
        return {"error": f"Erro na análise: {response.status_code}"}
    except Exception as e:
        logger.error(f"Erro ao analisar imagem: {str(e)}")
        return {"error": str(e)}


@tool("Buscar informações de preço e avaliações")
def buscar_info_produto(nome_produto: str, marca: str = None) -> Dict[str, Any]:
    """
    Busca informações adicionais sobre o produto (preços, avaliações, aceitação).
    
    Args:
        nome_produto: Nome do produto
        marca: Marca do produto (opcional)
    
    Returns:
        dict: Informações enriquecidas (preço sugerido, avaliações, etc.)
    """
    # Aqui você pode integrar com APIs de busca de preços, reviews, etc.
    # Por enquanto, retorna estrutura vazia para ser preenchida
    return {
        "preco_sugerido": None,
        "avaliacoes": None,
        "aceitacao": None,
        "informacoes_adicionais": {}
    }


@tool("Validar dados do produto")
def validar_dados_produto(dados_produto: Dict[str, Any]) -> Dict[str, Any]:
    """
    Valida a completude e qualidade dos dados do produto.
    
    Args:
        dados_produto: Dados do produto no formato modelo.json
    
    Returns:
        dict: Relatório de validação e dados corrigidos
    """
    validacao = {
        "valido": True,
        "campos_obrigatorios": [],
        "campos_faltantes": [],
        "sugestoes": []
    }
    
    # Validar estrutura básica
    if 'produto' not in dados_produto:
        validacao["valido"] = False
        validacao["campos_faltantes"].append("produto")
    
    produto = dados_produto.get('produto', {})
    
    # Campos obrigatórios
    campos_obrigatorios = ['nome', 'marca', 'categoria']
    for campo in campos_obrigatorios:
        if not produto.get(campo):
            validacao["campos_obrigatorios"].append(f"produto.{campo}")
            validacao["valido"] = False
    
    # Sugestões
    if not produto.get('descricao'):
        validacao["sugestoes"].append("Adicionar descrição detalhada do produto")
    
    if not produto.get('imagens') or len(produto.get('imagens', [])) == 0:
        validacao["sugestoes"].append("Adicionar pelo menos uma imagem do produto")
    
    return validacao


@tool("Gerar texto de anúncio")
def gerar_anuncio(dados_produto: Dict[str, Any]) -> str:
    """
    Gera texto de anúncio para WhatsApp/Marketplace baseado nos dados do produto.
    
    Args:
        dados_produto: Dados completos do produto
    
    Returns:
        str: Texto do anúncio formatado
    """
    produto = dados_produto.get('produto', {})
    nome = produto.get('nome', 'Produto')
    marca = produto.get('marca', '')
    descricao = produto.get('descricao', '')
    categoria = produto.get('categoria', '')
    
    preco = dados_produto.get('produto_viagem', {}).get('preco_venda_brl')
    
    anuncio = f"🛍️ *{nome}*"
    if marca:
        anuncio += f"\n🏷️ Marca: {marca}"
    if categoria:
        anuncio += f"\n📂 Categoria: {categoria}"
    if descricao:
        anuncio += f"\n\n{descricao}"
    if preco:
        anuncio += f"\n\n💰 *Preço: R$ {preco:.2f}*"
    
    anuncio += "\n\n💬 Interessado? Entre em contato!"
    
    return anuncio


# ============================================================================
# AGENTES CREWAI
# ============================================================================

def criar_agente_analise() -> Agent:
    """Cria agente especializado em análise de imagens de produtos"""
    if not CREWAI_AVAILABLE:
        return None
    
    # Obter LLM configurado com OpenMind.org
    llm = get_openmind_llm(temperature=0.7)
    
    return Agent(
        role='Analista de Produtos',
        goal='Extrair informações completas de produtos a partir de imagens',
        backstory="""Você é um especialista em análise de produtos comerciais.
        Sua expertise inclui identificação de marcas, categorias, características
        técnicas e códigos de barras a partir de imagens de embalagens.""",
        tools=[analisar_imagem_openmind],
        llm=llm,  # Usar LLM via OpenMind.org
        verbose=True,
        allow_delegation=False
    )


def criar_agente_enriquecimento() -> Agent:
    """Cria agente especializado em enriquecer dados de produtos"""
    if not CREWAI_AVAILABLE:
        return None
    
    llm = get_openmind_llm(temperature=0.7)
    
    return Agent(
        role='Especialista em Enriquecimento de Dados',
        goal='Buscar e adicionar informações complementares sobre produtos',
        backstory="""Você é um especialista em pesquisa de produtos no mercado.
        Você busca preços, avaliações, aceitação do mercado e informações
        adicionais que tornam o catálogo mais completo e útil.""",
        tools=[buscar_info_produto],
        llm=llm,  # Usar LLM via OpenMind.org
        verbose=True,
        allow_delegation=False
    )


def criar_agente_validacao() -> Agent:
    """Cria agente especializado em validação de dados"""
    if not CREWAI_AVAILABLE:
        return None
    
    llm = get_openmind_llm(temperature=0.3)  # Temperatura menor para validação mais precisa
    
    return Agent(
        role='Validador de Dados',
        goal='Validar qualidade, completude e consistência dos dados de produtos',
        backstory="""Você é um especialista em garantia de qualidade de dados.
        Você verifica se todos os campos obrigatórios estão preenchidos,
        se os dados são consistentes e se atendem aos padrões de qualidade.""",
        tools=[validar_dados_produto],
        llm=llm,  # Usar LLM via OpenMind.org
        verbose=True,
        allow_delegation=False
    )


def criar_agente_geracao() -> Agent:
    """Cria agente especializado em gerar anúncios"""
    if not CREWAI_AVAILABLE:
        return None
    
    llm = get_openmind_llm(temperature=0.8)  # Temperatura maior para criatividade
    
    return Agent(
        role='Criador de Anúncios',
        goal='Criar textos atraentes e informativos para anúncios de produtos',
        backstory="""Você é um copywriter especializado em marketing de produtos.
        Você cria textos persuasivos, informativos e bem formatados para
        anúncios em WhatsApp, marketplaces e redes sociais.""",
        tools=[gerar_anuncio],
        llm=llm,  # Usar LLM via OpenMind.org
        verbose=True,
        allow_delegation=False
    )


# ============================================================================
# CREWS (EQUIPES DE AGENTES)
# ============================================================================

def criar_crew_analise_completa() -> Crew:
    """
    Cria uma equipe de agentes para análise completa de produtos.
    
    Fluxo:
    1. Analisar imagem → 2. Enriquecer dados → 3. Validar → 4. Gerar anúncio
    """
    if not CREWAI_AVAILABLE:
        return None
    
    # Criar agentes
    agente_analise = criar_agente_analise()
    agente_enriquecimento = criar_agente_enriquecimento()
    agente_validacao = criar_agente_validacao()
    agente_geracao = criar_agente_geracao()
    
    # Criar tarefas
    tarefa_analise = Task(
        description="""Analise a imagem do produto fornecida e extraia todas as
        informações visíveis: nome, marca, categoria, descrição, código de barras,
        características técnicas e qualquer outro dado relevante.""",
        agent=agente_analise,
        expected_output="Dados do produto no formato modelo.json"
    )
    
    tarefa_enriquecimento = Task(
        description="""Baseado nos dados extraídos, busque informações adicionais:
        preços sugeridos, avaliações, aceitação do mercado e outras informações
        relevantes que enriqueçam o catálogo.""",
        agent=agente_enriquecimento,
        expected_output="Dados enriquecidos com preços, avaliações e informações adicionais"
    )
    
    tarefa_validacao = Task(
        description="""Valide os dados do produto verificando:
        1. Se todos os campos obrigatórios estão preenchidos
        2. Se os dados são consistentes e coerentes
        3. Se há campos que precisam ser completados ou corrigidos""",
        agent=agente_validacao,
        expected_output="Relatório de validação com dados corrigidos e sugestões"
    )
    
    tarefa_geracao = Task(
        description="""Gere um texto de anúncio atraente e informativo para o produto.
        O anúncio deve ser adequado para WhatsApp e marketplaces, incluindo:
        nome do produto, marca, descrição, preço (se disponível) e call-to-action.""",
        agent=agente_geracao,
        expected_output="Texto completo do anúncio formatado e pronto para uso"
    )
    
    # Criar crew (equipe)
    crew = Crew(
        agents=[agente_analise, agente_enriquecimento, agente_validacao, agente_geracao],
        tasks=[tarefa_analise, tarefa_enriquecimento, tarefa_validacao, tarefa_geracao],
        process=Process.sequential,  # Execução sequencial
        verbose=True
    )
    
    return crew


def criar_crew_analise_rapida() -> Crew:
    """
    Cria uma equipe simplificada para análise rápida (apenas análise e validação).
    """
    if not CREWAI_AVAILABLE:
        return None
    
    agente_analise = criar_agente_analise()
    agente_validacao = criar_agente_validacao()
    
    tarefa_analise = Task(
        description="Analise a imagem do produto e extraia informações básicas.",
        agent=agente_analise,
        expected_output="Dados básicos do produto"
    )
    
    tarefa_validacao = Task(
        description="Valide os dados extraídos e identifique campos faltantes.",
        agent=agente_validacao,
        expected_output="Dados validados com relatório de qualidade"
    )
    
    crew = Crew(
        agents=[agente_analise, agente_validacao],
        tasks=[tarefa_analise, tarefa_validacao],
        process=Process.sequential,
        verbose=True
    )
    
    return crew


# ============================================================================
# FUNÇÕES DE ALTO NÍVEL PARA USO NO DJANGO
# ============================================================================

def analisar_produto_com_crew(image_path: str, modo_completo: bool = True) -> Dict[str, Any]:
    """
    Analisa um produto usando CrewAI (orquestração de agentes).
    
    Args:
        image_path: Caminho da imagem do produto
        modo_completo: Se True, usa análise completa (4 agentes). Se False, análise rápida (2 agentes)
    
    Returns:
        dict: Resultado completo da análise
    """
    if not CREWAI_AVAILABLE:
        return {
            "success": False,
            "error": "CrewAI não está instalado. Execute: pip install crewai"
        }
    
    try:
        # Criar crew apropriado
        if modo_completo:
            crew = criar_crew_analise_completa()
        else:
            crew = criar_crew_analise_rapida()
        
        # Executar análise
        inputs = {
            "image_path": image_path
        }
        
        result = crew.kickoff(inputs=inputs)
        
        return {
            "success": True,
            "result": result,
            "mode": "complete" if modo_completo else "quick"
        }
    
    except Exception as e:
        logger.error(f"Erro ao executar crew: {str(e)}", exc_info=True)
        return {
            "success": False,
            "error": str(e)
        }


def processar_produto_com_multiplos_agentes(
    image_paths: List[str],
    incluir_anuncio: bool = True
) -> Dict[str, Any]:
    """
    Processa múltiplas imagens usando CrewAI com orquestração inteligente.
    
    Args:
        image_paths: Lista de caminhos das imagens
        incluir_anuncio: Se True, inclui geração de anúncio
    
    Returns:
        dict: Resultados consolidados
    """
    if not CREWAI_AVAILABLE:
        return {
            "success": False,
            "error": "CrewAI não está instalado"
        }
    
    resultados = []
    
    for image_path in image_paths:
        resultado = analisar_produto_com_crew(
            image_path,
            modo_completo=incluir_anuncio
        )
        resultados.append({
            "image_path": image_path,
            "result": resultado
        })
    
    # Consolidar resultados (mesma lógica que já existe em services.py)
    # ...
    
    return {
        "success": True,
        "resultados_individuais": resultados,
        "total_imagens": len(image_paths)
    }

