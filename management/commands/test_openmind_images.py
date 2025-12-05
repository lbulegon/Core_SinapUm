#!/usr/bin/env python3
"""
Script para testar o OpenMind avaliando imagens.
Este script demonstra como o OpenMind processa e avalia imagens usando a API.
"""

import asyncio
import logging
import os
from pathlib import Path

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

async def test_openmind_image_evaluation():
    """
    Testa a avaliação de imagens usando o OpenMind.
    """
    print("=" * 80)
    print("TESTE DE AVALIAÇÃO DE IMAGENS COM OPENMIND")
    print("=" * 80)
    
    # Verificar se há API key configurada
    api_key = os.environ.get("OM1_API_KEY")
    if not api_key:
        print("\n⚠️  AVISO: OM1_API_KEY não configurada")
        print("   Os testes usarão respostas mock quando necessário")
        print("   Para usar a API real do OpenMind, configure:")
        print("   export OM1_API_KEY='sua_chave_aqui'")
        print("   Ou obtenha uma chave gratuita em: portal.openmind.org\n")
    else:
        print(f"\n✅ API Key do OpenMind configurada")
        print(f"   Base URL: https://api.openmind.org/api/core/openai\n")
    
    # Adicionar caminho do OpenMind ao sys.path
    OM1_DIR = Path("/root/openmind_ws/OM1")
    if OM1_DIR.exists():
        import sys
        sys.path.insert(0, str(OM1_DIR))
    
    # Informações sobre os testes disponíveis - apontar para o OpenMind
    BASE_DIR = OM1_DIR if OM1_DIR.exists() else Path(__file__).parent
    test_cases_dir = BASE_DIR / "tests/integration/data/test_cases"
    images_dir = BASE_DIR / "tests/integration/data/images"
    
    print("📁 CASOS DE TESTE DISPONÍVEIS:")
    print("-" * 80)
    
    if test_cases_dir.exists():
        test_files = list(test_cases_dir.glob("*.json5"))
        for i, test_file in enumerate(test_files, 1):
            print(f"{i}. {test_file.stem}")
    
    print("\n🖼️  IMAGENS DE TESTE DISPONÍVEIS:")
    print("-" * 80)
    
    if images_dir.exists():
        image_files = list(images_dir.glob("*.jpg")) + list(images_dir.glob("*.png"))
        for i, img_file in enumerate(image_files, 1):
            size = img_file.stat().st_size / 1024  # KB
            print(f"{i}. {img_file.name} ({size:.1f} KB)")
    
    print("\n" + "=" * 80)
    print("FLUXO DE AVALIAÇÃO DE IMAGENS NO OPENMIND:")
    print("=" * 80)
    print("""
1. 📸 CAPTURA DE IMAGEM
   - Imagem é carregada do sistema de arquivos ou câmera
   - Convertida para formato base64 se necessário

2. 🔍 PROCESSAMENTO VLM (Vision Language Model)
   - Imagem é enviada para a API do OpenMind
   - API: https://api.openmind.org/api/core/openai
   - Modelo: gpt-4o-mini (com suporte a visão)
   - Retorna descrição textual da imagem

3. 🧠 PROCESSAMENTO LLM (Large Language Model)
   - Descrição da imagem é combinada com contexto do agente
   - Sistema gera ações baseadas no que foi detectado
   - Ações incluem: movimento, emoção, fala

4. ✅ AVALIAÇÃO
   - Compara ações geradas com expectativas
   - Verifica detecção de keywords
   - Avalia movimento e emoção apropriados
    """)
    
    print("=" * 80)
    print("PARA EXECUTAR OS TESTES:")
    print("=" * 80)
    print("""
# Teste específico com COCO (detecção local):
TEST_CASE="coco_indoor_detection" python -m pytest -m "integration" \\
    tests/integration/test_case_runner.py::test_specific_case -v -s

# Teste com OpenAI VLM (via API OpenMind):
TEST_CASE="open_ai_indoor_test" python -m pytest -m "integration" \\
    tests/integration/test_case_runner.py::test_specific_case -v -s

# Teste com Gemini VLM (via API OpenMind):
TEST_CASE="gemini_indoor_test" python -m pytest -m "integration" \\
    tests/integration/test_case_runner.py::test_specific_case -v -s

# Teste com VILA VLM (via API OpenMind):
TEST_CASE="vila_indoor_test" python -m pytest -m "integration" \\
    tests/integration/test_case_runner.py::test_specific_case -v -s

# Executar todos os testes de integração:
python -m pytest -m "integration" tests/integration/test_case_runner.py -v
    """)
    
    print("=" * 80)

if __name__ == "__main__":
    asyncio.run(test_openmind_image_evaluation())

