#!/usr/bin/env python3
"""
Script para testar a leitura de imagens e a geração de JSON no OpenMind.
Este script valida:
1. Carregamento de imagens de teste
2. Processamento das imagens
3. Geração de JSON de resposta
4. Validação do formato e conteúdo do JSON
"""

import asyncio
import json
import logging
import os
from pathlib import Path
from typing import Any, Dict, List, Optional

import json5
from PIL import Image

# Adicionar caminho do OpenMind ao sys.path ANTES dos imports
OM1_DIR = Path("/root/openmind_ws/OM1")
if OM1_DIR.exists():
    sys.path.insert(0, str(OM1_DIR))

# Imports do OpenMind - devem vir depois de adicionar ao sys.path
from tests.integration.mock_inputs.data_providers.mock_image_provider import (
    get_image_provider,
    load_test_images,
)
from tests.integration.test_case_runner import (
    load_test_case,
    load_test_images_from_config,
    run_test_case,
)

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

# Diretórios - apontar para o OpenMind
BASE_DIR = OM1_DIR if OM1_DIR.exists() else Path(__file__).parent
TEST_CASES_DIR = BASE_DIR / "tests/integration/data/test_cases"
IMAGES_DIR = BASE_DIR / "tests/integration/data/images"


class ImageJSONTester:
    """Classe para testar leitura de imagens e geração de JSON."""
    
    def __init__(self):
        self.test_results = []
        self.images_loaded = []
        self.json_outputs = []
    
    def test_image_loading(self, image_paths: List[str]) -> Dict[str, Any]:
        """
        Testa o carregamento de imagens.
        
        Parameters
        ----------
        image_paths : List[str]
            Lista de caminhos para as imagens
            
        Returns
        -------
        Dict[str, Any]
            Resultados do teste de carregamento
        """
        logger.info("=" * 80)
        logger.info("TESTE 1: CARREGAMENTO DE IMAGENS")
        logger.info("=" * 80)
        
        results = {
            "test_name": "image_loading",
            "images_tested": [],
            "success_count": 0,
            "error_count": 0,
            "errors": []
        }
        
        for img_path in image_paths:
            img_file = Path(img_path)
            if not img_file.is_absolute():
                img_file = IMAGES_DIR / img_path.replace("../images/", "")
            
            logger.info(f"\n📸 Testando imagem: {img_file.name}")
            
            try:
                # Verificar se o arquivo existe
                if not img_file.exists():
                    error_msg = f"Arquivo não encontrado: {img_file}"
                    logger.error(f"❌ {error_msg}")
                    results["errors"].append(error_msg)
                    results["error_count"] += 1
                    continue
                
                # Carregar imagem
                image = Image.open(img_file)
                
                # Obter informações da imagem
                width, height = image.size
                mode = image.mode
                file_size = img_file.stat().st_size
                
                logger.info(f"✅ Imagem carregada com sucesso!")
                logger.info(f"   - Dimensões: {width}x{height} pixels")
                logger.info(f"   - Modo: {mode}")
                logger.info(f"   - Tamanho do arquivo: {file_size / 1024:.2f} KB")
                
                image_info = {
                    "path": str(img_file),
                    "name": img_file.name,
                    "width": width,
                    "height": height,
                    "mode": mode,
                    "file_size_kb": round(file_size / 1024, 2),
                    "status": "success"
                }
                
                results["images_tested"].append(image_info)
                results["success_count"] += 1
                self.images_loaded.append(image)
                
            except Exception as e:
                error_msg = f"Erro ao carregar {img_file.name}: {str(e)}"
                logger.error(f"❌ {error_msg}")
                results["errors"].append(error_msg)
                results["error_count"] += 1
        
        logger.info(f"\n📊 Resumo do teste de carregamento:")
        logger.info(f"   - Imagens carregadas com sucesso: {results['success_count']}")
        logger.info(f"   - Erros: {results['error_count']}")
        
        return results
    
    def test_image_provider_integration(self, images: List[Image.Image]) -> Dict[str, Any]:
        """
        Testa a integração com o MockImageProvider.
        
        Parameters
        ----------
        images : List[Image.Image]
            Lista de imagens PIL carregadas
            
        Returns
        -------
        Dict[str, Any]
            Resultados do teste
        """
        logger.info("\n" + "=" * 80)
        logger.info("TESTE 2: INTEGRAÇÃO COM IMAGE PROVIDER")
        logger.info("=" * 80)
        
        results = {
            "test_name": "image_provider_integration",
            "images_provided": len(images),
            "images_retrieved": 0,
            "status": "success",
            "errors": []
        }
        
        try:
            # Carregar imagens no provider
            load_test_images(images)
            logger.info(f"✅ {len(images)} imagens carregadas no MockImageProvider")
            
            # Obter o provider
            provider = get_image_provider()
            
            # Testar recuperação de imagens
            retrieved_count = 0
            while True:
                image = provider.get_next_image()
                if image is None:
                    break
                retrieved_count += 1
                logger.info(f"   - Imagem {retrieved_count} recuperada: {image.size}")
            
            results["images_retrieved"] = retrieved_count
            
            if retrieved_count == len(images):
                logger.info(f"✅ Todas as {retrieved_count} imagens foram recuperadas corretamente")
            else:
                error_msg = f"Esperado {len(images)} imagens, mas apenas {retrieved_count} foram recuperadas"
                logger.warning(f"⚠️  {error_msg}")
                results["errors"].append(error_msg)
                results["status"] = "warning"
            
            # Resetar o provider
            provider.reset()
            logger.info("✅ Provider resetado com sucesso")
            
        except Exception as e:
            error_msg = f"Erro na integração com ImageProvider: {str(e)}"
            logger.error(f"❌ {error_msg}")
            results["errors"].append(error_msg)
            results["status"] = "error"
        
        return results
    
    async def test_json_generation(self, test_case_name: str) -> Dict[str, Any]:
        """
        Testa a geração de JSON através de um caso de teste.
        
        Parameters
        ----------
        test_case_name : str
            Nome do caso de teste a executar
            
        Returns
        -------
        Dict[str, Any]
            Resultados do teste incluindo o JSON gerado
        """
        logger.info("\n" + "=" * 80)
        logger.info(f"TESTE 3: GERAÇÃO DE JSON - {test_case_name}")
        logger.info("=" * 80)
        
        results = {
            "test_name": "json_generation",
            "test_case": test_case_name,
            "status": "pending",
            "json_generated": False,
            "json_content": None,
            "actions_count": 0,
            "errors": []
        }
        
        try:
            # Encontrar o arquivo de teste
            test_case_path = None
            for path in TEST_CASES_DIR.glob("*.json5"):
                config = load_test_case(path)
                if config.get("name") == test_case_name:
                    test_case_path = path
                    break
            
            if not test_case_path:
                error_msg = f"Caso de teste não encontrado: {test_case_name}"
                logger.error(f"❌ {error_msg}")
                results["errors"].append(error_msg)
                results["status"] = "error"
                return results
            
            logger.info(f"📄 Carregando caso de teste: {test_case_path.name}")
            config = load_test_case(test_case_path)
            
            logger.info(f"📋 Nome: {config.get('name')}")
            logger.info(f"📝 Descrição: {config.get('description')}")
            
            # Carregar imagens se necessário
            if "images" in config.get("input", {}):
                images = load_test_images_from_config(config)
                logger.info(f"📸 Imagens carregadas: {len(images)}")
                load_test_images(images)
            
            logger.info("🚀 Executando caso de teste...")
            test_results = await run_test_case(config)
            
            # Validar JSON gerado
            actions = test_results.get("actions", [])
            raw_response = test_results.get("raw_response")
            
            results["actions_count"] = len(actions)
            results["has_raw_response"] = raw_response is not None
            
            logger.info(f"\n📊 Resultados obtidos:")
            logger.info(f"   - Ações geradas: {len(actions)}")
            logger.info(f"   - Resposta bruta disponível: {raw_response is not None}")
            
            # Converter ações para JSON
            actions_json = []
            for i, action in enumerate(actions):
                action_dict = {
                    "index": i + 1,
                    "type": getattr(action, "type", "unknown"),
                    "value": getattr(action, "value", None)
                }
                actions_json.append(action_dict)
                logger.info(f"   - Ação {i+1}: {action_dict['type']} = {action_dict['value']}")
            
            json_output = {
                "test_case": test_case_name,
                "actions": actions_json,
                "actions_count": len(actions),
                "raw_response_available": raw_response is not None,
                "raw_response_length": len(raw_response) if raw_response else 0
            }
            
            results["json_content"] = json_output
            results["json_generated"] = True
            results["status"] = "success"
            
            logger.info(f"\n✅ JSON gerado com sucesso!")
            logger.info(f"   - Total de ações: {len(actions_json)}")
            
            # Validar estrutura do JSON
            validation_result = self.validate_json_structure(json_output)
            results["json_validation"] = validation_result
            
            self.json_outputs.append(json_output)
            
        except Exception as e:
            error_msg = f"Erro ao gerar JSON: {str(e)}"
            logger.error(f"❌ {error_msg}")
            results["errors"].append(error_msg)
            results["status"] = "error"
            import traceback
            logger.error(traceback.format_exc())
        
        return results
    
    def validate_json_structure(self, json_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Valida a estrutura do JSON gerado.
        
        Parameters
        ----------
        json_data : Dict[str, Any]
            Dados JSON para validar
            
        Returns
        -------
        Dict[str, Any]
            Resultados da validação
        """
        logger.info("\n" + "-" * 80)
        logger.info("VALIDAÇÃO DA ESTRUTURA DO JSON")
        logger.info("-" * 80)
        
        validation = {
            "valid": True,
            "errors": [],
            "warnings": []
        }
        
        # Verificar campos obrigatórios
        required_fields = ["test_case", "actions", "actions_count"]
        for field in required_fields:
            if field not in json_data:
                validation["errors"].append(f"Campo obrigatório ausente: {field}")
                validation["valid"] = False
        
        # Validar ações
        if "actions" in json_data:
            actions = json_data["actions"]
            if not isinstance(actions, list):
                validation["errors"].append("Campo 'actions' deve ser uma lista")
                validation["valid"] = False
            else:
                for i, action in enumerate(actions):
                    if not isinstance(action, dict):
                        validation["errors"].append(f"Ação {i+1} deve ser um dicionário")
                        validation["valid"] = False
                    else:
                        if "type" not in action:
                            validation["warnings"].append(f"Ação {i+1} não tem campo 'type'")
                        if "value" not in action:
                            validation["warnings"].append(f"Ação {i+1} não tem campo 'value'")
        
        # Validar contagem de ações
        if "actions_count" in json_data and "actions" in json_data:
            expected_count = len(json_data["actions"])
            actual_count = json_data["actions_count"]
            if expected_count != actual_count:
                validation["warnings"].append(
                    f"Contagem de ações inconsistente: esperado {expected_count}, "
                    f"obtido {actual_count}"
                )
        
        # Exibir resultados
        if validation["valid"]:
            logger.info("✅ Estrutura do JSON é válida")
        else:
            logger.error("❌ Estrutura do JSON possui erros")
        
        if validation["errors"]:
            for error in validation["errors"]:
                logger.error(f"   - {error}")
        
        if validation["warnings"]:
            for warning in validation["warnings"]:
                logger.warning(f"   ⚠️  {warning}")
        
        return validation
    
    def save_json_output(self, output_file: str = "test_output.json"):
        """
        Salva o JSON gerado em um arquivo.
        
        Parameters
        ----------
        output_file : str
            Nome do arquivo de saída
        """
        if not self.json_outputs:
            logger.warning("Nenhum JSON para salvar")
            return
        
        output_path = BASE_DIR / output_file
        
        try:
            output_data = {
                "test_summary": {
                    "total_tests": len(self.json_outputs),
                    "timestamp": str(Path(__file__).stat().st_mtime)
                },
                "results": self.json_outputs
            }
            
            with open(output_path, "w", encoding="utf-8") as f:
                json.dump(output_data, f, indent=2, ensure_ascii=False)
            
            logger.info(f"\n💾 JSON salvo em: {output_path}")
            
        except Exception as e:
            logger.error(f"❌ Erro ao salvar JSON: {str(e)}")
    
    def generate_report(self) -> str:
        """
        Gera um relatório resumido dos testes.
        
        Returns
        -------
        str
            Relatório em formato texto
        """
        report_lines = [
            "\n" + "=" * 80,
            "RELATÓRIO DE TESTES - LEITURA DE IMAGENS E GERAÇÃO DE JSON",
            "=" * 80,
            "",
            f"📊 Total de testes executados: {len(self.test_results)}",
            f"🖼️  Imagens carregadas: {len(self.images_loaded)}",
            f"📄 JSONs gerados: {len(self.json_outputs)}",
            "",
            "=" * 80,
        ]
        
        for result in self.test_results:
            test_name = result.get("test_name", "unknown")
            status = result.get("status", "unknown")
            
            status_icon = "✅" if status == "success" else "❌" if status == "error" else "⚠️"
            
            report_lines.append(f"\n{status_icon} {test_name}: {status}")
            
            if "errors" in result and result["errors"]:
                report_lines.append("   Erros:")
                for error in result["errors"]:
                    report_lines.append(f"      - {error}")
        
        report_lines.append("\n" + "=" * 80)
        
        return "\n".join(report_lines)


async def main():
    """Função principal para executar os testes."""
    print("=" * 80)
    print("TESTES DE LEITURA DE IMAGENS E GERAÇÃO DE JSON")
    print("=" * 80)
    print()
    
    tester = ImageJSONTester()
    
    # Teste 1: Carregamento de imagens
    logger.info("Iniciando Teste 1: Carregamento de Imagens")
    image_paths = [
        "../images/indoor_1.jpg",
        "../images/indoor_2.jpg"
    ]
    
    loading_result = tester.test_image_loading(image_paths)
    tester.test_results.append(loading_result)
    
    # Teste 2: Integração com Image Provider
    if tester.images_loaded:
        logger.info("\nIniciando Teste 2: Integração com Image Provider")
        provider_result = tester.test_image_provider_integration(tester.images_loaded)
        tester.test_results.append(provider_result)
    
    # Teste 3: Geração de JSON com diferentes casos de teste
    test_cases = [
        "coco_indoor_detection",
        "open_ai_indoor_test",
    ]
    
    for test_case in test_cases:
        logger.info(f"\nIniciando Teste 3: Geração de JSON - {test_case}")
        json_result = await tester.test_json_generation(test_case)
        tester.test_results.append(json_result)
    
    # Salvar JSON gerado
    tester.save_json_output("test_image_json_output.json")
    
    # Gerar relatório
    report = tester.generate_report()
    print(report)
    
    # Salvar relatório
    report_path = BASE_DIR / "test_image_json_report.txt"
    with open(report_path, "w", encoding="utf-8") as f:
        f.write(report)
    
    logger.info(f"\n📄 Relatório salvo em: {report_path}")
    
    print("\n" + "=" * 80)
    print("TESTES CONCLUÍDOS")
    print("=" * 80)


if __name__ == "__main__":
    asyncio.run(main())

