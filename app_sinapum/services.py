"""
Serviços para integração com OpenMind AI
"""
import requests
import logging
from django.conf import settings
from .utils import transform_evora_to_modelo_json

logger = logging.getLogger(__name__)

OPENMIND_AI_URL = getattr(settings, 'OPENMIND_AI_URL', 'http://127.0.0.1:8000')
OPENMIND_AI_KEY = getattr(settings, 'OPENMIND_AI_KEY', None)


def analyze_image_with_openmind(image_file):
    """
    Analisa uma imagem usando o OpenMind AI Server.
    
    Args:
        image_file: Arquivo de imagem (Django UploadedFile)
    
    Returns:
        dict: Resposta da API do OpenMind AI
    """
    try:
        url = f"{OPENMIND_AI_URL}/api/v1/analyze-product-image"
        
        headers = {}
        if OPENMIND_AI_KEY:
            headers['Authorization'] = f'Bearer {OPENMIND_AI_KEY}'
        
        files = {
            'image': (image_file.name, image_file.read(), image_file.content_type)
        }
        
        logger.info(f"Enviando imagem para análise: {image_file.name}")
        response = requests.post(url, files=files, headers=headers, timeout=60)
        
        # Verificar se a resposta é JSON válido
        content_type = response.headers.get('Content-Type', '')
        
        if response.status_code == 200:
            try:
                # Verificar se o Content-Type indica JSON
                if 'application/json' in content_type:
                    result = response.json()
                    logger.info(f"Análise concluída com sucesso: {result.get('success', False)}")
                    
                    # Transformar dados ÉVORA para formato modelo.json
                    if result.get('success') and result.get('data'):
                        try:
                            modelo_json = transform_evora_to_modelo_json(
                                result['data'],
                                image_file.name
                            )
                            # Substituir data pelo formato modelo.json
                            result['data'] = modelo_json
                            logger.info("Dados transformados para formato modelo.json")
                        except Exception as transform_error:
                            logger.error(f"Erro ao transformar dados: {str(transform_error)}", exc_info=True)
                            # Continuar com dados originais se houver erro na transformação
                    
                    return result
                else:
                    # Tentar parsear mesmo sem Content-Type correto
                    try:
                        result = response.json()
                        logger.info(f"Análise concluída com sucesso: {result.get('success', False)}")
                        
                        # Transformar dados ÉVORA para formato modelo.json
                        if result.get('success') and result.get('data'):
                            try:
                                modelo_json = transform_evora_to_modelo_json(
                                    result['data'],
                                    image_file.name
                                )
                                result['data'] = modelo_json
                                logger.info("Dados transformados para formato modelo.json")
                            except Exception as transform_error:
                                logger.error(f"Erro ao transformar dados: {str(transform_error)}", exc_info=True)
                        
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
