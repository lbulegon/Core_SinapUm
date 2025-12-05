#!/usr/bin/env python3
"""
Script simplificado para testar rapidamente a leitura de imagens e geração de JSON.
Executa testes básicos sem depender de toda a infraestrutura de testes de integração.

Este script está localizado em /root/SinapUm/management/commands mas acessa
os recursos do OpenMind em /root/openmind_ws/OM1
"""

import asyncio
import json
import logging
import sys
from pathlib import Path
from typing import Dict, Any, List

# Adicionar caminho do OpenMind ao sys.path
OM1_DIR = Path("/root/openmind_ws/OM1")
if OM1_DIR.exists():
    sys.path.insert(0, str(OM1_DIR))

try:
    from PIL import Image
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False
    print("⚠️  AVISO: PIL/Pillow não está disponível. Algumas funcionalidades estarão limitadas.")
    print("   Instale com: pip install Pillow")

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


def get_om1_base_dir() -> Path:
    """Retorna o diretório base do OpenMind OM1."""
    om1_dir = Path("/root/openmind_ws/OM1")
    if om1_dir.exists():
        return om1_dir
    raise FileNotFoundError("Diretório do OpenMind não encontrado: /root/openmind_ws/OM1")


def test_image_reading(image_path: Path) -> Dict[str, Any]:
    """
    Testa a leitura de uma imagem.
    
    Parameters
    ----------
    image_path : Path
        Caminho para a imagem
        
    Returns
    -------
    Dict[str, Any]
        Informações sobre a imagem lida
    """
    logger.info(f"📸 Testando leitura da imagem: {image_path.name}")
    
    result = {
        "image_path": str(image_path),
        "exists": False,
        "readable": False,
        "width": None,
        "height": None,
        "mode": None,
        "size_kb": None,
        "error": None
    }
    
    try:
        # Verificar se existe
        if not image_path.exists():
            result["error"] = f"Arquivo não encontrado: {image_path}"
            logger.error(f"❌ {result['error']}")
            return result
        
        result["exists"] = True
        
        # Obter tamanho do arquivo
        file_size = image_path.stat().st_size
        result["size_kb"] = round(file_size / 1024, 2)
        
        if not PIL_AVAILABLE:
            result["error"] = "PIL/Pillow não está disponível para ler a imagem"
            logger.error(f"❌ {result['error']}")
            return result
        
        # Tentar abrir a imagem
        with Image.open(image_path) as img:
            width, height = img.size
            mode = img.mode
            
            result["readable"] = True
            result["width"] = width
            result["height"] = height
            result["mode"] = mode
            
            logger.info(f"✅ Imagem lida com sucesso!")
            logger.info(f"   - Dimensões: {width}x{height} pixels")
            logger.info(f"   - Modo: {mode}")
            logger.info(f"   - Tamanho: {result['size_kb']} KB")
            
            # Validar formato
            valid_formats = ["JPEG", "PNG", "RGB"]
            if img.format not in valid_formats and mode not in ["RGB", "RGBA", "L"]:
                logger.warning(f"⚠️  Formato não padrão: {img.format}")
            
            return result
            
    except Exception as e:
        result["error"] = f"Erro ao ler imagem: {str(e)}"
        logger.error(f"❌ {result['error']}")
        return result


def test_multiple_images(image_paths: List[str], base_dir: Path) -> List[Dict[str, Any]]:
    """
    Testa a leitura de múltiplas imagens.
    
    Parameters
    ----------
    image_paths : List[str]
        Lista de caminhos para imagens
    base_dir : Path
        Diretório base para caminhos relativos
        
    Returns
    -------
    List[Dict[str, Any]]
        Lista de resultados para cada imagem
    """
    logger.info("=" * 80)
    logger.info("TESTE DE LEITURA DE MÚLTIPLAS IMAGENS")
    logger.info("=" * 80)
    
    results = []
    
    for img_path_str in image_paths:
        img_path = Path(img_path_str)
        
        # Resolver caminho relativo
        if not img_path.is_absolute():
            # Remover "../images/" se presente
            clean_path = img_path_str.replace("../images/", "")
            img_path = base_dir / "tests/integration/data/images" / clean_path
        
        result = test_image_reading(img_path)
        results.append(result)
    
    # Resumo
    successful = sum(1 for r in results if r.get("readable", False))
    total = len(results)
    
    logger.info(f"\n📊 Resumo:")
    logger.info(f"   - Total de imagens: {total}")
    logger.info(f"   - Lidas com sucesso: {successful}")
    logger.info(f"   - Falhas: {total - successful}")
    
    return results


def generate_test_json(image_results: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Gera um JSON de teste baseado nos resultados das imagens.
    
    Parameters
    ----------
    image_results : List[Dict[str, Any]]
        Resultados da leitura das imagens
        
    Returns
    -------
    Dict[str, Any]
        JSON gerado com informações sobre as imagens
    """
    logger.info("\n" + "=" * 80)
    logger.info("GERAÇÃO DE JSON DE TESTE")
    logger.info("=" * 80)
    
    json_data = {
        "test_type": "image_reading_and_json_generation",
        "timestamp": str(Path(__file__).stat().st_mtime),
        "images_processed": len(image_results),
        "images": []
    }
    
    for i, result in enumerate(image_results):
        image_info = {
            "index": i + 1,
            "path": result.get("image_path", "unknown"),
            "status": "success" if result.get("readable") else "error",
            "dimensions": {
                "width": result.get("width"),
                "height": result.get("height")
            },
            "mode": result.get("mode"),
            "size_kb": result.get("size_kb")
        }
        
        if result.get("error"):
            image_info["error"] = result["error"]
        
        json_data["images"].append(image_info)
        
        logger.info(f"\n📄 Imagem {i+1}:")
        logger.info(f"   - Status: {image_info['status']}")
        if image_info['status'] == 'success':
            logger.info(f"   - Dimensões: {image_info['dimensions']['width']}x{image_info['dimensions']['height']}")
            logger.info(f"   - Tamanho: {image_info['size_kb']} KB")
        else:
            logger.info(f"   - Erro: {image_info.get('error', 'Desconhecido')}")
    
    # Validar JSON
    try:
        json_string = json.dumps(json_data, indent=2, ensure_ascii=False)
        logger.info(f"\n✅ JSON gerado com sucesso!")
        logger.info(f"   - Tamanho do JSON: {len(json_string)} caracteres")
        
        # Verificar estrutura
        validation = validate_json_structure(json_data)
        json_data["validation"] = validation
        
        return json_data
        
    except Exception as e:
        logger.error(f"❌ Erro ao gerar JSON: {str(e)}")
        return {"error": str(e)}


def validate_json_structure(json_data: Dict[str, Any]) -> Dict[str, Any]:
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
    required_fields = ["test_type", "images_processed", "images"]
    for field in required_fields:
        if field not in json_data:
            validation["errors"].append(f"Campo obrigatório ausente: {field}")
            validation["valid"] = False
    
    # Validar lista de imagens
    if "images" in json_data:
        images = json_data["images"]
        if not isinstance(images, list):
            validation["errors"].append("Campo 'images' deve ser uma lista")
            validation["valid"] = False
        else:
            for i, img in enumerate(images):
                if not isinstance(img, dict):
                    validation["errors"].append(f"Imagem {i+1} deve ser um dicionário")
                    validation["valid"] = False
                else:
                    # Verificar campos esperados na imagem
                    expected_img_fields = ["index", "path", "status"]
                    for field in expected_img_fields:
                        if field not in img:
                            validation["warnings"].append(
                                f"Imagem {i+1} não tem campo '{field}'"
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


def save_json_file(json_data: Dict[str, Any], output_path: Path) -> bool:
    """
    Salva o JSON em um arquivo.
    
    Parameters
    ----------
    json_data : Dict[str, Any]
        Dados JSON para salvar
    output_path : Path
        Caminho do arquivo de saída
        
    Returns
    -------
    bool
        True se salvou com sucesso, False caso contrário
    """
    try:
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(json_data, f, indent=2, ensure_ascii=False)
        
        logger.info(f"\n💾 JSON salvo em: {output_path}")
        logger.info(f"   - Tamanho do arquivo: {output_path.stat().st_size / 1024:.2f} KB")
        return True
        
    except Exception as e:
        logger.error(f"❌ Erro ao salvar JSON: {str(e)}")
        return False


async def main():
    """Função principal."""
    print("=" * 80)
    print("TESTE SIMPLIFICADO - LEITURA DE IMAGENS E GERAÇÃO DE JSON")
    print("=" * 80)
    print()
    
    try:
        # Obter diretório base do OpenMind
        base_dir = get_om1_base_dir()
        logger.info(f"📁 Diretório base do OpenMind: {base_dir}")
    except FileNotFoundError as e:
        logger.error(f"❌ {e}")
        sys.exit(1)
    
    # Lista de imagens para testar
    image_paths = [
        "../images/indoor_1.jpg",
        "../images/indoor_2.jpg"
    ]
    
    # Teste 1: Leitura de imagens
    logger.info("INICIANDO TESTE DE LEITURA DE IMAGENS\n")
    image_results = test_multiple_images(image_paths, base_dir)
    
    # Teste 2: Geração de JSON
    logger.info("\nINICIANDO TESTE DE GERAÇÃO DE JSON\n")
    json_data = generate_test_json(image_results)
    
    # Teste 3: Salvar JSON
    if "error" not in json_data:
        output_file = Path(__file__).parent / "test_image_json_output_simple.json"
        logger.info("\nSALVANDO JSON EM ARQUIVO\n")
        save_json_file(json_data, output_file)
    
    # Resumo final
    print("\n" + "=" * 80)
    print("RESUMO DOS TESTES")
    print("=" * 80)
    
    successful_images = sum(1 for r in image_results if r.get("readable", False))
    total_images = len(image_results)
    
    print(f"✅ Imagens lidas: {successful_images}/{total_images}")
    
    if "error" not in json_data:
        json_valid = json_data.get("validation", {}).get("valid", False)
        print(f"✅ JSON gerado: {'Sim' if json_valid else 'Não'}")
        print(f"✅ Validação do JSON: {'Passou' if json_valid else 'Falhou'}")
    else:
        print(f"❌ Erro ao gerar JSON: {json_data.get('error')}")
    
    print("=" * 80)
    
    # Retornar código de saída apropriado
    if successful_images == total_images and "error" not in json_data:
        sys.exit(0)
    else:
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())

