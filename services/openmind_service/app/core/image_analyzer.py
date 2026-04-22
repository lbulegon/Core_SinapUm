"""
Analisador de imagens usando IA via OpenMind.org
"""
import logging
import requests
import json
import re
from typing import Dict, Any, Union, Optional
from pathlib import Path
import base64
from io import BytesIO
from PIL import Image
from app.core.config import settings

logger = logging.getLogger(__name__)


class ImageAnalyzer:
    """Classe para análise de imagens usando modelos de IA via OpenMind.org"""
    
    def __init__(self):
        """Inicializar analisador"""
        # Usar apenas OpenMind.org (sem OpenAI)
        self.api_key = settings.OPENMIND_AI_API_KEY
        if not self.api_key:
            raise ValueError("OPENMIND_AI_API_KEY não configurada")
        
        # URL base do OpenMind.org (endpoint válido atual).
        self.base_url = getattr(settings, 'OPENMIND_ORG_BASE_URL', 'https://api.openmind.com/api/core/openai')
        self.model = getattr(settings, 'OPENMIND_ORG_MODEL', 'gpt-4o')
        
        logger.info(f"Inicializado ImageAnalyzer com OpenMind.org | Base URL: {self.base_url} | Modelo: {self.model}")
        
    async def analyze(
        self,
        image_data: Union[bytes, str],
        prompt: str = None,
        params: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        Analisa uma imagem e retorna informações estruturadas
        
        Args:
            image_data: Dados da imagem (bytes ou URL)
            prompt: Prompt para análise (OBRIGATÓRIO - deve vir do banco de dados)
            
        Returns:
            Dict com informações da análise
        """
        try:
            # Se for URL, baixar imagem
            if isinstance(image_data, str) and image_data.startswith("http"):
                response = requests.get(image_data, timeout=30)
                response.raise_for_status()
                image_data = response.content
            
            # Converter para base64 se necessário
            if isinstance(image_data, bytes):
                image_base64 = base64.b64encode(image_data).decode('utf-8')
            else:
                raise ValueError("Dados de imagem inválidos")
            
            # Validar que o prompt foi fornecido
            if not prompt or not prompt.strip():
                error_msg = "Prompt não fornecido. O prompt deve ser obtido do banco de dados através do Django."
                logger.error(error_msg)
                raise ValueError(error_msg)
            
            # Usar prompt fornecido (do banco de dados ou fallback)
            analysis_prompt = prompt.strip()
            logger.info(f"✅ Usando prompt fornecido (tamanho: {len(analysis_prompt)} caracteres)")
            
            # Chamar API do OpenMind.org (compatível com OpenAI Vision)
            logger.info("Enviando imagem para análise via OpenMind.org API")
            
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            # Preparar mensagem para API
            messages = [
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": analysis_prompt
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{image_base64}"
                            }
                        }
                    ]
                }
            ]
            
            # Usar parâmetros do prompt se fornecidos, senão usar padrões otimizados
            max_tokens = params.get('max_tokens', 2500) if params else 2500  # Reduzido de 4000 para 2500
            temperature = params.get('temperature', 0.3) if params else 0.3
            
            payload = {
                "model": self.model,
                "messages": messages,
                "max_tokens": max_tokens,
                "temperature": temperature
            }
            
            # Usa a base configurada e corrige domínio legado (.org -> .com).
            base = str(self.base_url).rstrip("/")
            if "api.openmind.org" in base:
                base = base.replace("api.openmind.org", "api.openmind.com")
            api_url = f"{base}/chat/completions"
            
            logger.info(f"🚀 Enviando para OpenMind.org: {api_url} | max_tokens={max_tokens}, temperature={temperature}")
            
            # Timeout otimizado: 30 segundos (reduzido de 60)
            response = requests.post(
                api_url,
                headers=headers,
                json=payload,
                timeout=30
            )
            
            if response.status_code != 200:
                error_detail = response.text
                try:
                    error_json = response.json()
                    if isinstance(error_json.get('error'), dict):
                        error_detail = error_json['error'].get('message', str(error_json))
                    else:
                        error_detail = str(error_json)
                except:
                    pass
                error_msg = f"Erro na API OpenMind.org (status {response.status_code}): {error_detail[:200]}"
                logger.error(error_msg)
                raise Exception(error_msg)
            
            logger.info(f"✅ Resposta recebida de: {api_url}")
            
            api_response = response.json()
            
            # Extrair resposta do modelo
            if "choices" not in api_response or len(api_response["choices"]) == 0:
                raise Exception("Resposta da API sem choices")
            
            content = api_response["choices"][0]["message"]["content"]
            
            # Log da resposta bruta (primeiros 1000 caracteres para debug)
            logger.info(f"📥 Resposta bruta da API (primeiros 1000 chars): {content[:1000]}")
            logger.info(f"📥 Tamanho total da resposta: {len(content)} caracteres")
            
            # Tentar parsear JSON da resposta
            # A resposta pode vir com markdown code blocks
            content_clean = content.strip()
            if content_clean.startswith("```"):
                # Remover markdown code blocks
                lines = content_clean.split("\n")
                content_clean = "\n".join(lines[1:-1]) if len(lines) > 2 else content_clean
            if content_clean.startswith("```json"):
                content_clean = content_clean[7:]
            if content_clean.endswith("```"):
                content_clean = content_clean[:-3]
            content_clean = content_clean.strip()
            
            try:
                # Tentar parsear como JSON
                result = json.loads(content_clean)
                logger.info("✅ JSON parseado com sucesso")
                # Log detalhado do resultado para debug
                logger.info(f"📊 Resultado parseado - Chaves: {list(result.keys())}")
                logger.info(f"📊 Nome: '{result.get('nome', 'N/A')}', Marca: '{result.get('marca', 'N/A')}', Categoria: '{result.get('categoria', 'N/A')}'")
                logger.info(f"📊 Descrição (primeiros 200 chars): '{result.get('descricao', 'N/A')[:200]}'")
                
                # Verificar se o resultado está vazio ou genérico
                nome_val = result.get('nome', '').strip()
                marca_val = result.get('marca', '').strip()
                if not nome_val or nome_val.lower() in ['produto não identificado', 'n/a', '']:
                    logger.warning("⚠️ ATENÇÃO: Campo 'nome' está vazio ou genérico na resposta da API!")
                if not marca_val or marca_val.lower() in ['marca não identificada', 'n/a', '']:
                    logger.warning("⚠️ ATENÇÃO: Campo 'marca' está vazio ou genérico na resposta da API!")
            except json.JSONDecodeError as e:
                # Se não for JSON válido, tentar extrair JSON do texto
                logger.warning(f"Resposta não é JSON puro, tentando extrair: {str(e)}")
                # Procurar por JSON no texto
                json_match = re.search(r'\{.*\}', content_clean, re.DOTALL)
                if json_match:
                    try:
                        result = json.loads(json_match.group())
                    except:
                        # Fallback: criar estrutura básica com o texto
                        result = {
                            "nome": "Produto Analisado",
                            "descricao": content_clean[:500] if len(content_clean) > 500 else content_clean,
                            "categoria": "Geral",
                            "texto_extraido": content_clean,
                            "erro_parse": "Resposta não pôde ser parseada como JSON completo"
                        }
                else:
                    # Último fallback
                    result = {
                        "nome": "Produto Analisado",
                        "descricao": content_clean[:500] if len(content_clean) > 500 else content_clean,
                        "categoria": "Geral",
                        "texto_extraido": content_clean,
                        "erro_parse": "Não foi possível extrair JSON da resposta"
                    }
            
            # Garantir que campos essenciais existam
            # Mas verificar se o prompt pediu para não usar valores genéricos
            prompt_proibe_genericos = "NUNCA use" in analysis_prompt or "não use" in analysis_prompt.lower()
            
            if "nome" not in result or not result.get("nome") or result.get("nome", "").strip() == "":
                if prompt_proibe_genericos:
                    logger.error("❌ ERRO: Prompt proíbe valores genéricos, mas API retornou 'nome' vazio!")
                result["nome"] = "Produto não identificado"
            if "descricao" not in result or not result.get("descricao") or result.get("descricao", "").strip() == "":
                if prompt_proibe_genericos:
                    logger.error("❌ ERRO: Prompt proíbe valores genéricos, mas API retornou 'descricao' vazia!")
                result["descricao"] = "Descrição não disponível"
            if "categoria" not in result or not result.get("categoria") or result.get("categoria", "").strip() == "":
                if prompt_proibe_genericos:
                    logger.error("❌ ERRO: Prompt proíbe valores genéricos, mas API retornou 'categoria' vazia!")
                result["categoria"] = "Geral"
            
            # Adicionar metadados
            result["imagem_processada"] = True
            result["modelo_ia"] = self.model
            result["timestamp"] = str(Path(__file__).stat().st_mtime) if Path(__file__).exists() else None
            
            logger.info(f"Análise concluída: {result.get('nome', 'N/A')} - {result.get('categoria', 'N/A')}")
            return result
            
        except Exception as e:
            logger.error(f"Erro ao analisar imagem: {str(e)}", exc_info=True)
            raise

