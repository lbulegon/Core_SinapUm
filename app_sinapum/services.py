"""
Serviços para integração com OpenMind AI
"""
import base64
import json
import requests
import logging
from django.conf import settings
from .utils import transform_evora_to_modelo_json
from .models import PromptTemplate

logger = logging.getLogger(__name__)

OPENMIND_AI_URL = getattr(settings, 'OPENMIND_AI_URL', 'http://127.0.0.1:8000')
OPENMIND_AI_KEY = getattr(settings, 'OPENMIND_AI_KEY', None)
USE_MCP_FOR_ANALYZE = getattr(settings, 'USE_MCP_FOR_ANALYZE', True)

# Prompt fallback mínimo (usado apenas quando não há prompt no banco de dados)
# Este é um prompt genérico básico para garantir que o sistema funcione
# RECOMENDA-SE sempre cadastrar prompts específicos no admin para melhor qualidade
FALLBACK_PROMPT_ANALISE_PRODUTO = (
    "Analise esta imagem de produto e retorne um JSON estruturado com todas as informações visíveis. "
    "Inclua: nome, descrição, categoria, marca, código de barras (se visível), preço (se visível), "
    "características, especificações técnicas, cores, materiais e qualquer outra informação relevante. "
    "Seja detalhado e extraia todas as informações possíveis da imagem."
)


def _build_openmind_image_base_urls():
    """Monta lista de bases candidatas para endpoint de análise de imagem (fonte única)."""
    def _is_cloud_openmind(raw: str) -> bool:
        value = str(raw or "").strip().lower()
        return ("api.openmind.com" in value) or ("api.openmind.org" in value)

    candidates = [
        getattr(settings, 'OPENMIND_IMAGE_URL', None),
        getattr(settings, 'OPENMIND_BASE_URL', None),
        'http://openmind:8001',
    ]
    bases = []
    for raw in candidates:
        if not raw:
            continue
        if _is_cloud_openmind(raw):
            continue
        base = str(raw).strip().rstrip('/')
        if base and base not in bases:
            bases.append(base)
    return bases


def _analyze_image_via_mcp(image_file, image_path=None, image_url=None):
    """
    Analisa imagem via MCP Tool Registry (vitrinezap.analisar_produto).
    Usa prompt versionado do Tool Registry.
    
    Returns:
        dict: Resultado no formato OpenMind (success, data, etc) ou None se falhar
    """
    try:
        from app_mcp_tool_registry.services import execute_tool
        from app_mcp_tool_registry.models import Tool
        
        # Verificar se a tool existe
        if not Tool.objects.filter(name='vitrinezap.analisar_produto', is_active=True).exists():
            logger.warning("Tool vitrinezap.analisar_produto não registrada")
            strict_mcp = getattr(settings, 'ANALYZE_IMAGE_MCP_STRICT', True)
            if strict_mcp:
                return {
                    'success': False,
                    'error': 'Tool MCP vitrinezap.analisar_produto não registrada',
                    'error_code': 'MCP_TOOL_NOT_REGISTERED',
                }
            return None
        
        image_file.seek(0)
        image_data = image_file.read()
        image_base64 = base64.b64encode(image_data).decode('utf-8')
        
        input_data = {
            'image_base64': image_base64,
            'prompt_params': {}
        }
        if image_url:
            input_data['image_url'] = image_url
        
        result = execute_tool(
            tool_name='vitrinezap.analisar_produto',
            input_data=input_data,
            client_key='vitrinezap',
        )
        
        if not result.get('ok'):
            logger.warning(f"MCP execute falhou: {result.get('error')}; fallback para legado")
            strict_mcp = getattr(settings, 'ANALYZE_IMAGE_MCP_STRICT', True)
            if strict_mcp:
                return {
                    'success': False,
                    'error': result.get('error') or 'Falha na execução MCP para análise de imagem',
                    'error_code': 'MCP_ANALYZE_EXECUTION_FAILED',
                }
            return None
        
        output = result.get('output') or {}
        if not output.get('success'):
            strict_mcp = getattr(settings, 'ANALYZE_IMAGE_MCP_STRICT', True)
            if strict_mcp:
                return {
                    'success': False,
                    'error': output.get('error') or 'MCP retornou falha na análise de imagem',
                    'error_code': output.get('error_code', 'MCP_ANALYZE_FAILED'),
                }
            return None
        
        # Adicionar image_path/image_url ao retorno
        if image_path:
            output['image_path'] = image_path
        if image_url:
            output['image_url'] = image_url
        
        logger.info("✅ Análise via MCP (vitrinezap.analisar_produto) concluída")
        return output
        
    except Exception as e:
        logger.warning(f"Erro ao usar MCP para análise: {e}; fallback para legado", exc_info=True)
        strict_mcp = getattr(settings, 'ANALYZE_IMAGE_MCP_STRICT', True)
        if strict_mcp:
            return {
                'success': False,
                'error': f'Erro ao usar MCP para análise: {e}',
                'error_code': 'MCP_ANALYZE_EXCEPTION',
            }
        return None


def analyze_image_with_openmind(image_file, image_path=None, image_url=None, prompt=None):
    """
    Analisa uma imagem usando o OpenMind AI Server.
    
    Quando USE_MCP_FOR_ANALYZE=True, tenta primeiro via MCP Tool Registry (vitrinezap.analisar_produto).
    Se a tool não existir ou falhar, usa fluxo legado (OpenMind direto).
    
    Args:
        image_file: Arquivo de imagem (Django UploadedFile)
        image_path: Caminho relativo da imagem salva (ex: "media/uploads/uuid.jpg")
        image_url: URL completa da imagem (ex: "http://host:port/media/uploads/uuid.jpg")
        prompt: Prompt customizado (opcional). Se None, busca do banco de dados.
    
    Returns:
        dict: Resposta da API do OpenMind AI com image_url e image_path incluídos se fornecidos
    """
    if USE_MCP_FOR_ANALYZE:
        mcp_result = _analyze_image_via_mcp(image_file, image_path=image_path, image_url=image_url)
        if mcp_result is not None:
            image_file.seek(0)
            if mcp_result.get('success') and mcp_result.get('data'):
                prompt_info = mcp_result.get('data', {}).get('cadastro_meta', {}).get('prompt_usado') or {
                    'nome': 'MCP Tool Registry',
                    'versao': 'N/A',
                    'fonte': 'vitrinezap.analisar_produto',
                }
                try:
                    modelo_json = transform_evora_to_modelo_json(
                        mcp_result['data'],
                        image_filename=image_file.name,
                        image_path=image_path,
                        prompt_info=prompt_info,
                    )
                    mcp_result['data'] = modelo_json
                    mcp_result['prompt_info'] = prompt_info
                except Exception as te:
                    logger.warning(f"Erro ao transformar dados MCP: {te}")
            return mcp_result
        strict_mcp = getattr(settings, 'ANALYZE_IMAGE_MCP_STRICT', True)
        if strict_mcp:
            return {
                'success': False,
                'error': 'Fluxo MCP obrigatório: análise sem fallback legado',
                'error_code': 'MCP_ONLY_ENFORCED',
            }
        image_file.seek(0)
    
    try:
        # Inicializar prompt_info como None
        prompt_info = None
        
        # Buscar prompt do banco de dados se não foi fornecido
        if prompt is None:
            # Primeiro tentar buscar global (sem sistema) - mais confiável
            prompt_template = PromptTemplate.get_prompt_ativo('analise_imagem_produto', sistema=None)
            
            # Se não encontrou global, tentar sistema específico
            if not prompt_template:
                sistema_codigo = getattr(settings, 'SISTEMA_CODIGO', 'evora')
                logger.info(f"Prompt não encontrado globalmente, tentando sistema '{sistema_codigo}'...")
                try:
                    prompt_template = PromptTemplate.get_prompt_ativo('analise_imagem_produto', sistema=sistema_codigo)
                except:
                    prompt_template = None
            
            if prompt_template:
                prompt = prompt_template.get_prompt_text_com_parametros()
                sistema_nome = prompt_template.sistema.nome if prompt_template.sistema else 'Global (sem sistema)'
                # Extrair parâmetros do prompt se disponíveis
                prompt_params = prompt_template.parametros if hasattr(prompt_template, 'parametros') and prompt_template.parametros else {}
                # Armazenar informações do prompt para incluir no cadastro_meta
                prompt_info = {
                    'nome': prompt_template.nome,
                    'versao': prompt_template.versao,
                    'fonte': 'PostgreSQL',
                    'sistema': sistema_nome,
                    'tipo_prompt': prompt_template.tipo_prompt,
                    'parametros': prompt_params
                }
                logger.info(
                    f"✅ [PROMPT DO BANCO] Sistema: {sistema_nome} | "
                    f"Prompt: {prompt_template.nome} (v{prompt_template.versao}) | "
                    f"Tipo: analise_imagem_produto | "
                    f"Parâmetros: {prompt_params}"
                )
            else:
                # Fallback: prompt genérico mínimo (apenas para garantir que o sistema funcione)
                prompt = FALLBACK_PROMPT_ANALISE_PRODUTO
                prompt_params = {}  # Sem parâmetros quando usa fallback
                prompt_info = {
                    'nome': 'FALLBACK',
                    'versao': '1.0.0',
                    'fonte': 'Código (fallback)',
                    'sistema': None,
                    'tipo_prompt': 'analise_imagem_produto',
                    'parametros': {}
                }
                
                warning_msg = (
                    f"⚠️ [FALLBACK ATIVO] Nenhum prompt ativo encontrado no banco de dados!\n"
                    f"   Sistema buscado: '{sistema_codigo}' e globalmente\n"
                    f"   Tipo de prompt: 'analise_imagem_produto'\n"
                    f"   Ação: Usando prompt fallback genérico mínimo\n"
                    f"   ⚠️ RECOMENDAÇÃO: Cadastre um prompt específico no admin Django para melhor qualidade das análises.\n"
                    f"   📍 Acesse: Admin > Templates de Prompts > Adicionar novo prompt"
                )
                logger.warning(warning_msg)
                # Também logar no console para visibilidade
                print(f"\n{'='*80}\n{warning_msg}\n{'='*80}\n")
        else:
            # Se prompt foi fornecido como parâmetro, criar prompt_info básico
            prompt_info = {
                'nome': 'Fornecido como parâmetro',
                'versao': 'N/A',
                'fonte': 'Parâmetro da função',
                'sistema': None,
                'tipo_prompt': 'analise_imagem_produto',
                'parametros': {}
            }
        
        # Garantir que prompt_info existe mesmo se não foi definido acima
        if prompt_info is None:
            prompt_info = {
                'nome': 'Desconhecido',
                'versao': 'N/A',
                'fonte': 'Não informado',
                'sistema': None,
                'tipo_prompt': 'analise_imagem_produto',
                'parametros': {}
            }
        
        headers = {}
        if OPENMIND_AI_KEY:
            headers['Authorization'] = f'Bearer {OPENMIND_AI_KEY}'
        
        # Prompt deve sempre estar presente (vem do banco ou fallback)
        if not prompt or not prompt.strip():
            error_msg = "Prompt não encontrado. Não é possível analisar a imagem sem um prompt."
            logger.error(error_msg)
            return {
                'success': False,
                'error': error_msg,
                'error_code': 'PROMPT_REQUIRED'
            }
        
        # Adicionar prompt e parâmetros como form data
        data = {
            'prompt': prompt.strip()
        }
        # Adicionar parâmetros se disponíveis
        if prompt_params:
            data['prompt_params'] = json.dumps(prompt_params)
        
        # Verificar se está usando fallback para incluir no log
        is_fallback = prompt == FALLBACK_PROMPT_ANALISE_PRODUTO
        prompt_source = "FALLBACK" if is_fallback else "BANCO DE DADOS"
        
        logger.info(
            f"📤 Enviando imagem para análise: {image_file.name} | "
            f"Prompt: {prompt_source} ({len(prompt)} caracteres)"
        )

        image_bytes = image_file.read()
        image_content_type = image_file.content_type or 'application/octet-stream'
        response = None
        last_error = None

        # Timeout otimizado: 30 segundos (reduzido de 60)
        for base_url in _build_openmind_image_base_urls():
            url = f"{base_url}/api/v1/analyze-product-image"
            files = {
                'image': (image_file.name, image_bytes, image_content_type)
            }
            try:
                response = requests.post(url, files=files, data=data, headers=headers, timeout=30)
            except requests.exceptions.RequestException as request_error:
                last_error = request_error
                logger.warning("Falha ao conectar em %s: %s", url, request_error)
                continue

            # OpenMind cloud pode não expor este endpoint legado; tenta próximo candidato.
            if response.status_code in (404, 405, 501):
                logger.warning("Endpoint de imagem indisponível em %s (status=%s), tentando fallback", url, response.status_code)
                continue
            break

        if response is None:
            error_msg = f"Erro de conexão com OpenMind AI: {str(last_error) if last_error else 'nenhuma URL respondeu'}"
            logger.error(error_msg)
            return {
                'success': False,
                'error': error_msg,
                'error_code': 'CONNECTION_ERROR'
            }
        
        # Verificar se a resposta é JSON válido
        content_type = response.headers.get('Content-Type', '')
        
        if response.status_code == 200:
            try:
                # Verificar se o Content-Type indica JSON
                if 'application/json' in content_type:
                    result = response.json()
                    
                    # Adicionar informação sobre o prompt usado (se foi fallback)
                    if prompt == FALLBACK_PROMPT_ANALISE_PRODUTO:
                        result['prompt_used'] = 'fallback'
                        result['prompt_warning'] = (
                            'Este resultado foi gerado usando um prompt fallback genérico. '
                            'Para melhor qualidade, cadastre um prompt específico no admin Django.'
                        )
                    
                    logger.info(f"✅ Análise concluída com sucesso: {result.get('success', False)}")
                    
                    # Transformar dados ÉVORA para formato modelo.json
                    if result.get('success') and result.get('data'):
                        try:
                            # prompt_info já foi garantido acima, usar diretamente
                            modelo_json = transform_evora_to_modelo_json(
                                result['data'],
                                image_filename=image_file.name,
                                image_path=image_path,
                                prompt_info=prompt_info
                            )
                            # Substituir data pelo formato modelo.json
                            result['data'] = modelo_json
                            # Incluir prompt_info no retorno para referência (opcional)
                            result['prompt_info'] = prompt_info
                            logger.info("Dados transformados para formato modelo.json")
                        except Exception as transform_error:
                            logger.error(f"Erro ao transformar dados: {str(transform_error)}", exc_info=True)
                            # Continuar com dados originais se houver erro na transformação
                            # Mas ainda tentar incluir prompt_info
                            if 'prompt_info' in locals():
                                result['prompt_info'] = prompt_info
                    
                    # Adicionar image_url e image_path à resposta se fornecidos
                    if image_url:
                        result['image_url'] = image_url
                    if image_path:
                        result['image_path'] = image_path
                    
                    # Garantir que prompt_info está no retorno
                    if 'prompt_info' in locals() and 'prompt_info' not in result:
                        result['prompt_info'] = prompt_info
                    
                    return result
                else:
                    # Tentar parsear mesmo sem Content-Type correto
                    try:
                        result = response.json()
                        
                        # Adicionar informação sobre o prompt usado (se foi fallback)
                        if prompt == FALLBACK_PROMPT_ANALISE_PRODUTO:
                            result['prompt_used'] = 'fallback'
                            result['prompt_warning'] = (
                                'Este resultado foi gerado usando um prompt fallback genérico. '
                                'Para melhor qualidade, cadastre um prompt específico no admin Django.'
                            )
                        
                        logger.info(f"✅ Análise concluída com sucesso: {result.get('success', False)}")
                        
                        # Transformar dados ÉVORA para formato modelo.json
                        if result.get('success') and result.get('data'):
                            try:
                                modelo_json = transform_evora_to_modelo_json(
                                    result['data'],
                                    image_filename=image_file.name,
                                    image_path=image_path
                                )
                                result['data'] = modelo_json
                                logger.info("Dados transformados para formato modelo.json")
                            except Exception as transform_error:
                                logger.error(f"Erro ao transformar dados: {str(transform_error)}", exc_info=True)
                        
                        # Adicionar image_url e image_path à resposta se fornecidos
                        if image_url:
                            result['image_url'] = image_url
                        if image_path:
                            result['image_path'] = image_path
                        
                        return result
                    except ValueError:
                        # Resposta não é JSON - tratar como erro
                        response_text = response.text.strip()
                        logger.error(f"Resposta não-JSON recebida: {response_text}")
                        return {
                            'success': False,
                            'error': f"Resposta inesperada do servidor: {response_text}",
                            'error_code': 'INVALID_RESPONSE',
                            'raw_response': response_text
                        }
            except ValueError as json_error:
                # Erro ao parsear JSON
                response_text = response.text.strip()
                logger.error(f"Erro ao parsear JSON da resposta: {str(json_error)}. Conteúdo: {response_text}")
                return {
                    'success': False,
                    'error': f"Erro ao processar imagem: Erro ao parsear JSON da resposta: {str(json_error)}. Conteúdo: {response_text}",
                    'error_code': 'JSON_PARSE_ERROR',
                    'raw_response': response_text
                }
        else:
            # Status code diferente de 200
            response_text = response.text.strip()
            error_msg = f"Erro na API OpenMind AI (status {response.status_code}): {response_text}"
            logger.error(error_msg)
            return {
                'success': False,
                'error': error_msg,
                'error_code': 'API_ERROR',
                'status_code': response.status_code,
                'raw_response': response_text
            }
    
    except requests.exceptions.RequestException as e:
        error_msg = f"Erro de conexão com OpenMind AI: {str(e)}"
        logger.error(error_msg)
        return {
            'success': False,
            'error': error_msg,
            'error_code': 'CONNECTION_ERROR'
        }
    except Exception as e:
        error_msg = f"Erro inesperado: {str(e)}"
        logger.error(error_msg, exc_info=True)
        return {
            'success': False,
            'error': error_msg,
            'error_code': 'UNKNOWN_ERROR'
        }


def analyze_multiple_images(image_files):
    """
    Analisa múltiplas imagens e verifica se são do mesmo produto.
    
    Args:
        image_files: Lista de arquivos de imagem (Django UploadedFile)
    
    Returns:
        dict: Resultado da análise com informações sobre consistência dos produtos
    """
    results = []
    produtos_identificados = []
    
    for idx, image_file in enumerate(image_files):
        logger.info(f"Analisando imagem {idx + 1}/{len(image_files)}: {image_file.name}")
        
        # Resetar ponteiro do arquivo
        image_file.seek(0)
        
        # Analisar imagem
        result = analyze_image_with_openmind(image_file)
        
        if result.get('success') and result.get('data'):
            produto_data = result['data']
            produtos_identificados.append({
                'index': idx,
                'filename': image_file.name,
                'produto_data': produto_data
            })
        
        results.append({
            'index': idx,
            'filename': image_file.name,
            'result': result
        })
    
    # Verificar consistência dos produtos
    consistencia = verificar_consistencia_produtos(produtos_identificados)
    
    # Se todas as imagens são do mesmo produto, consolidar dados
    if consistencia['mesmo_produto'] and len(produtos_identificados) > 0:
        produto_consolidado = consolidar_produto_multiplas_imagens(produtos_identificados)
        return {
            'success': True,
            'mesmo_produto': True,
            'produto_consolidado': produto_consolidado,
            'analises_individuais': results,
            'consistencia': consistencia,
            'total_imagens': len(image_files)
        }
    else:
        # Produtos diferentes ou erro na análise
        return {
            'success': True,
            'mesmo_produto': False,
            'produtos_diferentes': produtos_identificados,
            'analises_individuais': results,
            'consistencia': consistencia,
            'total_imagens': len(image_files),
            'aviso': 'As imagens parecem ser de produtos diferentes. Verifique antes de salvar.'
        }


def verificar_consistencia_produtos(produtos_identificados):
    """
    Verifica se as imagens são do mesmo produto comparando nome, marca e código de barras.
    
    Args:
        produtos_identificados: Lista de dicionários com dados dos produtos identificados
    
    Returns:
        dict: Informações sobre consistência
    """
    if len(produtos_identificados) < 2:
        return {
            'mesmo_produto': True,
            'confianca': 1.0,
            'detalhes': 'Apenas uma imagem analisada'
        }
    
    # Extrair informações principais de cada produto
    produtos_info = []
    for prod in produtos_identificados:
        produto = prod['produto_data'].get('produto', {})
        produtos_info.append({
            'nome': produto.get('nome', '').lower().strip(),
            'marca': produto.get('marca', '').lower().strip(),
            'codigo_barras': produto.get('codigo_barras', ''),
            'categoria': produto.get('categoria', '').lower().strip()
        })
    
    # Comparar produtos
    mesmo_nome = all(p['nome'] == produtos_info[0]['nome'] for p in produtos_info if p['nome'])
    mesma_marca = all(p['marca'] == produtos_info[0]['marca'] for p in produtos_info if p['marca'])
    mesmo_codigo = all(p['codigo_barras'] == produtos_info[0]['codigo_barras'] for p in produtos_info if p['codigo_barras'] and produtos_info[0]['codigo_barras'])
    mesma_categoria = all(p['categoria'] == produtos_info[0]['categoria'] for p in produtos_info if p['categoria'])
    
    # Calcular confiança
    fatores = [mesmo_nome, mesma_marca, mesmo_codigo, mesma_categoria]
    confianca = sum(fatores) / len(fatores) if fatores else 0.0
    
    mesmo_produto = confianca >= 0.75  # 75% de similaridade
    
    return {
        'mesmo_produto': mesmo_produto,
        'confianca': confianca,
        'detalhes': {
            'mesmo_nome': mesmo_nome,
            'mesma_marca': mesma_marca,
            'mesmo_codigo_barras': mesmo_codigo,
            'mesma_categoria': mesma_categoria
        },
        'produtos_comparados': len(produtos_identificados)
    }


def consolidar_produto_multiplas_imagens(produtos_identificados):
    """
    Consolida dados de múltiplas imagens do mesmo produto.
    
    Args:
        produtos_identificados: Lista de produtos identificados (mesmo produto)
    
    Returns:
        dict: Produto consolidado com todas as imagens
    """
    if not produtos_identificados:
        return None
    
    # Usar o primeiro produto como base
    produto_base = produtos_identificados[0]['produto_data'].copy()
    
    # Coletar todas as imagens
    todas_imagens = []
    for prod in produtos_identificados:
        imagens = prod['produto_data'].get('produto', {}).get('imagens', [])
        todas_imagens.extend(imagens)
    
    # Remover duplicatas mantendo ordem
    imagens_unicas = []
    for img in todas_imagens:
        if img not in imagens_unicas:
            imagens_unicas.append(img)
    
    # Atualizar array de imagens
    if 'produto' in produto_base:
        produto_base['produto']['imagens'] = imagens_unicas
    
    # Atualizar fonte do cadastro_meta para indicar múltiplas imagens
    if 'cadastro_meta' in produto_base:
        total_imagens = len(produtos_identificados)
        produto_base['cadastro_meta']['fonte'] = f"Análise automática de {total_imagens} imagem(ns) do mesmo produto"
    
    return produto_base
