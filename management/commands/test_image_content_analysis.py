#!/usr/bin/env python3
"""
Script para testar a análise do conteúdo de imagens e geração de JSON baseado no conteúdo.
Este script:
1. Carrega imagens de teste
2. Analisa o conteúdo através de VLM (Vision Language Model)
3. Gera descrição textual do conteúdo
4. Processa a descrição através do LLM para gerar ações em JSON
5. Valida se o JSON reflete corretamente o conteúdo da imagem
"""

import asyncio
import base64
import json
import logging
import os
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

import json5
from PIL import Image

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

# Adicionar caminho do OpenMind ao sys.path
OM1_DIR = Path("/root/openmind_ws/OM1")
if OM1_DIR.exists():
    sys.path.insert(0, str(OM1_DIR))

# Diretórios - apontar para o OpenMind
BASE_DIR = OM1_DIR if OM1_DIR.exists() else Path(__file__).parent
TEST_CASES_DIR = BASE_DIR / "tests/integration/data/test_cases"
IMAGES_DIR = BASE_DIR / "tests/integration/data/images"


class ImageContentAnalyzer:
    """Classe para analisar conteúdo de imagens e validar geração de JSON."""
    
    def __init__(self):
        self.image_descriptions = []
        self.json_outputs = []
        self.validation_results = []
    
    def analyze_image_content_basic(self, image_path: Path) -> Dict[str, Any]:
        """
        Análise básica do conteúdo da imagem (metadados, formato, etc.).
        
        Parameters
        ----------
        image_path : Path
            Caminho para a imagem
            
        Returns
        -------
        Dict[str, Any]
            Informações básicas sobre a imagem
        """
        logger.info(f"📸 Analisando conteúdo básico da imagem: {image_path.name}")
        
        analysis = {
            "image_path": str(image_path),
            "image_name": image_path.name,
            "exists": False,
            "readable": False,
            "dimensions": None,
            "file_size_kb": None,
            "format": None,
            "mode": None,
            "content_analysis": {
                "has_content": False,
                "can_be_processed": False
            }
        }
        
        try:
            if not image_path.exists():
                analysis["error"] = f"Arquivo não encontrado: {image_path}"
                logger.error(f"❌ {analysis['error']}")
                return analysis
            
            analysis["exists"] = True
            
            # Obter informações do arquivo
            file_size = image_path.stat().st_size
            analysis["file_size_kb"] = round(file_size / 1024, 2)
            
            # Tentar abrir e analisar a imagem
            with Image.open(image_path) as img:
                width, height = img.size
                analysis["dimensions"] = {"width": width, "height": height}
                analysis["format"] = img.format
                analysis["mode"] = img.mode
                analysis["readable"] = True
                
                # Análise básica de conteúdo
                analysis["content_analysis"]["has_content"] = width > 0 and height > 0
                analysis["content_analysis"]["can_be_processed"] = (
                    analysis["content_analysis"]["has_content"] and
                    img.format in ["JPEG", "PNG"] and
                    img.mode in ["RGB", "RGBA", "L"]
                )
                
                logger.info(f"✅ Imagem analisada: {width}x{height}, formato: {img.format}")
                logger.info(f"   - Pode ser processada: {analysis['content_analysis']['can_be_processed']}")
        
        except Exception as e:
            analysis["error"] = f"Erro ao analisar imagem: {str(e)}"
            logger.error(f"❌ {analysis['error']}")
        
        return analysis
    
    async def analyze_image_content_with_vlm(
        self, 
        test_case_name: str
    ) -> Dict[str, Any]:
        """
        Analisa o conteúdo da imagem usando VLM e gera JSON através de caso de teste.
        
        Parameters
        ----------
        test_case_name : str
            Nome do caso de teste a executar
            
        Returns
        -------
        Dict[str, Any]
            Resultado completo da análise incluindo descrição VLM e JSON gerado
        """
        logger.info("\n" + "=" * 80)
        logger.info(f"ANÁLISE DE CONTEÚDO COM VLM - {test_case_name}")
        logger.info("=" * 80)
        
        result = {
            "test_case": test_case_name,
            "status": "pending",
            "image_analysis": None,
            "vlm_description": None,
            "json_actions": None,
            "content_validation": None,
            "errors": []
        }
        
        try:
            # Encontrar e carregar caso de teste
            test_case_path = None
            for path in TEST_CASES_DIR.glob("*.json5"):
                config = load_test_case(path)
                if config.get("name") == test_case_name:
                    test_case_path = path
                    break
            
            if not test_case_path:
                error_msg = f"Caso de teste não encontrado: {test_case_name}"
                logger.error(f"❌ {error_msg}")
                result["errors"].append(error_msg)
                result["status"] = "error"
                return result
            
            config = load_test_case(test_case_path)
            logger.info(f"📄 Caso de teste carregado: {config.get('name')}")
            
            # Analisar imagens do caso de teste
            if "images" not in config.get("input", {}):
                error_msg = "Caso de teste não possui imagens configuradas"
                logger.error(f"❌ {error_msg}")
                result["errors"].append(error_msg)
                result["status"] = "error"
                return result
            
            image_paths = config["input"]["images"]
            image_analyses = []
            
            logger.info(f"\n📸 Analisando {len(image_paths)} imagem(ns) do caso de teste:")
            
            for img_path_str in image_paths:
                img_path = Path(img_path_str)
                if not img_path.is_absolute():
                    clean_path = img_path_str.replace("../images/", "")
                    img_path = IMAGES_DIR / clean_path
                
                analysis = self.analyze_image_content_basic(img_path)
                image_analyses.append(analysis)
                
                if analysis.get("readable"):
                    logger.info(f"   ✅ {img_path.name}: {analysis['dimensions']}")
                else:
                    logger.warning(f"   ⚠️  {img_path.name}: não pôde ser lida")
            
            result["image_analysis"] = image_analyses
            
            # Carregar imagens para processamento
            images = load_test_images_from_config(config)
            if images:
                load_test_images(images)
                logger.info(f"✅ {len(images)} imagem(ns) carregada(s) no provider")
            
            # Executar caso de teste para obter análise VLM e JSON
            logger.info("\n🚀 Executando caso de teste para análise de conteúdo...")
            test_results = await run_test_case(config)
            
            # Extrair descrição VLM da resposta bruta
            raw_response = test_results.get("raw_response", "")
            if raw_response:
                result["vlm_description"] = self._extract_vlm_description(raw_response)
                logger.info(f"\n📝 Descrição VLM obtida:")
                if result["vlm_description"]:
                    logger.info(f"   {result['vlm_description'][:200]}...")
                else:
                    logger.warning("   ⚠️  Descrição VLM não encontrada na resposta")
            
            # Extrair ações JSON geradas
            actions = test_results.get("actions", [])
            result["json_actions"] = self._extract_json_actions(actions)
            
            logger.info(f"\n📋 Ações JSON geradas: {len(actions)} ação(ões)")
            for i, action in enumerate(actions, 1):
                action_type = getattr(action, "type", "unknown")
                action_value = getattr(action, "value", None)
                logger.info(f"   {i}. {action_type}: {action_value}")
            
            # Validar se o JSON reflete o conteúdo da imagem
            result["content_validation"] = self.validate_content_vs_json(
                image_analyses,
                result["vlm_description"],
                result["json_actions"]
            )
            
            result["status"] = "success"
            self.validation_results.append(result)
            
        except Exception as e:
            error_msg = f"Erro ao analisar conteúdo com VLM: {str(e)}"
            logger.error(f"❌ {error_msg}")
            result["errors"].append(error_msg)
            result["status"] = "error"
            import traceback
            logger.error(traceback.format_exc())
        
        return result
    
    def _extract_vlm_description(self, raw_response: str) -> Optional[str]:
        """
        Extrai a descrição VLM da resposta bruta.
        
        Parameters
        ----------
        raw_response : str
            Resposta bruta do sistema
            
        Returns
        -------
        Optional[str]
            Descrição VLM extraída ou None
        """
        if not raw_response:
            return None
        
        # Tentar encontrar descrição VLM na resposta
        # Formato comum: "INPUT: Vision\n// START\n{descrição}\n// END"
        if "// START" in raw_response and "// END" in raw_response:
            start_idx = raw_response.find("// START") + len("// START")
            end_idx = raw_response.find("// END")
            if start_idx < end_idx:
                description = raw_response[start_idx:end_idx].strip()
                if description:
                    return description
        
        # Se não encontrou no formato padrão, retornar parte da resposta
        # que parece ser descrição visual
        lines = raw_response.split("\n")
        for line in lines:
            if any(keyword in line.lower() for keyword in ["see", "detect", "image", "scene", "visual"]):
                return line.strip()
        
        return raw_response[:500] if len(raw_response) > 500 else raw_response
    
    def _extract_json_actions(self, actions: List) -> List[Dict[str, Any]]:
        """
        Extrai ações em formato JSON estruturado.
        
        Parameters
        ----------
        actions : List
            Lista de ações do sistema
            
        Returns
        -------
        List[Dict[str, Any]]
            Lista de ações em formato JSON
        """
        json_actions = []
        
        for i, action in enumerate(actions):
            action_dict = {
                "index": i + 1,
                "type": getattr(action, "type", "unknown"),
                "value": getattr(action, "value", None)
            }
            json_actions.append(action_dict)
        
        return json_actions
    
    def validate_content_vs_json(
        self,
        image_analyses: List[Dict[str, Any]],
        vlm_description: Optional[str],
        json_actions: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Valida se o JSON gerado reflete corretamente o conteúdo da imagem.
        
        Parameters
        ----------
        image_analyses : List[Dict[str, Any]]
            Análises das imagens
        vlm_description : Optional[str]
            Descrição gerada pelo VLM
        json_actions : List[Dict[str, Any]]
            Ações JSON geradas
            
        Returns
        -------
        Dict[str, Any]
            Resultado da validação
        """
        logger.info("\n" + "-" * 80)
        logger.info("VALIDAÇÃO: Conteúdo da Imagem vs JSON Gerado")
        logger.info("-" * 80)
        
        validation = {
            "valid": True,
            "score": 0.0,
            "checks": [],
            "warnings": [],
            "errors": []
        }
        
        # Check 1: Imagens foram analisadas
        readable_images = [a for a in image_analyses if a.get("readable", False)]
        if readable_images:
            validation["checks"].append({
                "check": "imagens_analisadas",
                "status": "pass",
                "message": f"{len(readable_images)} imagem(ns) analisada(s) com sucesso"
            })
            logger.info(f"✅ {len(readable_images)} imagem(ns) analisada(s)")
        else:
            validation["errors"].append("Nenhuma imagem pôde ser analisada")
            validation["valid"] = False
            logger.error("❌ Nenhuma imagem pôde ser analisada")
        
        # Check 2: Descrição VLM foi gerada
        if vlm_description:
            validation["checks"].append({
                "check": "vlm_description",
                "status": "pass",
                "message": f"Descrição VLM gerada ({len(vlm_description)} caracteres)"
            })
            validation["score"] += 0.3
            logger.info(f"✅ Descrição VLM gerada: {len(vlm_description)} caracteres")
        else:
            validation["warnings"].append("Descrição VLM não foi gerada")
            logger.warning("⚠️  Descrição VLM não foi gerada")
        
        # Check 3: Ações JSON foram geradas
        if json_actions:
            validation["checks"].append({
                "check": "json_actions",
                "status": "pass",
                "message": f"{len(json_actions)} ação(ões) JSON gerada(s)"
            })
            validation["score"] += 0.3
            logger.info(f"✅ {len(json_actions)} ação(ões) JSON gerada(s)")
            
            # Analisar tipos de ações
            action_types = [a.get("type") for a in json_actions]
            logger.info(f"   Tipos de ações: {', '.join(set(action_types))}")
        else:
            validation["errors"].append("Nenhuma ação JSON foi gerada")
            validation["valid"] = False
            logger.error("❌ Nenhuma ação JSON foi gerada")
        
        # Check 4: Relação entre descrição VLM e ações JSON
        if vlm_description and json_actions:
            # Verificar se há coerência básica
            vlm_lower = vlm_description.lower()
            
            # Verificar se a descrição menciona objetos comuns que podem gerar ações
            keywords_found = []
            common_keywords = ["dog", "cat", "person", "human", "object", "see"]
            
            for keyword in common_keywords:
                if keyword in vlm_lower:
                    keywords_found.append(keyword)
            
            if keywords_found:
                validation["checks"].append({
                    "check": "content_coherence",
                    "status": "pass",
                    "message": f"Coerência detectada: keywords {keywords_found}"
                })
                validation["score"] += 0.2
                logger.info(f"✅ Coerência de conteúdo: keywords detectados - {keywords_found}")
            else:
                validation["warnings"].append(
                    "Não foi possível verificar coerência entre descrição VLM e ações"
                )
                logger.warning("⚠️  Coerência não pôde ser verificada")
        
        # Check 5: Estrutura das ações JSON
        valid_action_types = ["move", "emotion", "speak"]
        valid_actions = [a for a in json_actions if a.get("type") in valid_action_types]
        
        if len(valid_actions) > 0:
            validation["checks"].append({
                "check": "json_structure",
                "status": "pass",
                "message": f"{len(valid_actions)} ação(ões) com estrutura válida"
            })
            validation["score"] += 0.2
            logger.info(f"✅ Estrutura JSON válida: {len(valid_actions)} ação(ões)")
        else:
            validation["warnings"].append("Ações JSON podem não estar no formato esperado")
            logger.warning("⚠️  Estrutura JSON pode estar incorreta")
        
        # Normalizar score (0.0 a 1.0)
        validation["score"] = min(validation["score"], 1.0)
        
        # Determinar se passou (score >= 0.5)
        if validation["score"] < 0.5:
            validation["valid"] = False
        
        logger.info(f"\n📊 Score de validação: {validation['score']:.2f}/1.0")
        logger.info(f"   Status: {'✅ PASSOU' if validation['valid'] else '❌ FALHOU'}")
        
        return validation
    
    def generate_content_analysis_report(self) -> str:
        """Gera relatório completo da análise de conteúdo."""
        report_lines = [
            "\n" + "=" * 80,
            "RELATÓRIO DE ANÁLISE DE CONTEÚDO DE IMAGENS",
            "=" * 80,
            "",
            f"📊 Total de análises: {len(self.validation_results)}",
            "",
        ]
        
        for i, result in enumerate(self.validation_results, 1):
            report_lines.append(f"\n{'=' * 80}")
            report_lines.append(f"ANÁLISE {i}: {result.get('test_case', 'unknown')}")
            report_lines.append("=" * 80)
            
            status = result.get("status", "unknown")
            status_icon = "✅" if status == "success" else "❌"
            report_lines.append(f"\n{status_icon} Status: {status}")
            
            # Informações da imagem
            image_analyses = result.get("image_analysis", [])
            if image_analyses:
                report_lines.append(f"\n📸 Imagens Analisadas: {len(image_analyses)}")
                for img_analysis in image_analyses:
                    if img_analysis.get("readable"):
                        dims = img_analysis.get("dimensions", {})
                        report_lines.append(
                            f"   - {img_analysis.get('image_name')}: "
                            f"{dims.get('width')}x{dims.get('height')}"
                        )
            
            # Descrição VLM
            vlm_desc = result.get("vlm_description")
            if vlm_desc:
                report_lines.append(f"\n📝 Descrição VLM:")
                report_lines.append(f"   {vlm_desc[:200]}...")
            
            # Ações JSON
            json_actions = result.get("json_actions", [])
            if json_actions:
                report_lines.append(f"\n📋 Ações JSON ({len(json_actions)}):")
                for action in json_actions:
                    report_lines.append(
                        f"   - {action.get('type')}: {action.get('value')}"
                    )
            
            # Validação
            validation = result.get("content_validation", {})
            if validation:
                score = validation.get("score", 0.0)
                valid = validation.get("valid", False)
                report_lines.append(f"\n✅ Validação:")
                report_lines.append(f"   - Score: {score:.2f}/1.0")
                report_lines.append(f"   - Status: {'PASSOU' if valid else 'FALHOU'}")
                
                checks = validation.get("checks", [])
                if checks:
                    report_lines.append(f"   - Checks realizados: {len(checks)}")
                    for check in checks:
                        status_icon = "✅" if check.get("status") == "pass" else "⚠️"
                        report_lines.append(
                            f"     {status_icon} {check.get('check')}: {check.get('message')}"
                        )
        
        report_lines.append("\n" + "=" * 80)
        
        return "\n".join(report_lines)
    
    def save_results_to_json(self, output_file: str = "image_content_analysis.json"):
        """Salva resultados da análise em arquivo JSON."""
        output_path = BASE_DIR / output_file
        
        output_data = {
            "analysis_summary": {
                "total_analyses": len(self.validation_results),
                "timestamp": str(Path(__file__).stat().st_mtime)
            },
            "results": self.validation_results
        }
        
        try:
            with open(output_path, "w", encoding="utf-8") as f:
                json.dump(output_data, f, indent=2, ensure_ascii=False)
            
            logger.info(f"\n💾 Resultados salvos em: {output_path}")
            return True
        except Exception as e:
            logger.error(f"❌ Erro ao salvar resultados: {str(e)}")
            return False


async def main():
    """Função principal."""
    print("=" * 80)
    print("TESTE DE ANÁLISE DE CONTEÚDO DE IMAGENS E GERAÇÃO DE JSON")
    print("=" * 80)
    print()
    
    analyzer = ImageContentAnalyzer()
    
    # Casos de teste para analisar
    test_cases = [
        "coco_indoor_detection",
        "open_ai_indoor_test",
    ]
    
    # Executar análises
    for test_case in test_cases:
        logger.info(f"\n{'=' * 80}")
        logger.info(f"Processando caso de teste: {test_case}")
        logger.info("=" * 80)
        
        result = await analyzer.analyze_image_content_with_vlm(test_case)
        
        if result.get("status") == "success":
            logger.info(f"\n✅ Análise completa para: {test_case}")
        else:
            logger.error(f"\n❌ Falha na análise para: {test_case}")
    
    # Gerar e exibir relatório
    report = analyzer.generate_content_analysis_report()
    print(report)
    
    # Salvar resultados
    analyzer.save_results_to_json("image_content_analysis.json")
    
    # Salvar relatório
    report_path = BASE_DIR / "image_content_analysis_report.txt"
    with open(report_path, "w", encoding="utf-8") as f:
        f.write(report)
    
    logger.info(f"\n📄 Relatório salvo em: {report_path}")
    
    print("\n" + "=" * 80)
    print("ANÁLISES CONCLUÍDAS")
    print("=" * 80)


if __name__ == "__main__":
    asyncio.run(main())

