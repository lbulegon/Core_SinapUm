#!/usr/bin/env python
"""
Script para verificar os caminhos de retorno das imagens
e identificar para qual pasta estão apontando.
"""

import os
import sys
import django
from pathlib import Path

# Configurar Django
sys.path.insert(0, str(Path(__file__).parent))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'setup.settings')
django.setup()

from django.conf import settings
from django.contrib.sites.models import Site

def verificar_configuracao_imagens():
    """Verifica a configuração atual de imagens"""
    print("=" * 80)
    print("VERIFICAÇÃO DE CONFIGURAÇÃO DE IMAGENS")
    print("=" * 80)
    print()
    
    # 1. Verificar MEDIA_ROOT
    print("1. CONFIGURAÇÕES DO DJANGO:")
    print(f"   MEDIA_ROOT: {settings.MEDIA_ROOT}")
    print(f"   MEDIA_URL: {settings.MEDIA_URL}")
    print(f"   BASE_DIR: {settings.BASE_DIR}")
    print()
    
    # 2. Verificar se MEDIA_ROOT existe
    print("2. VERIFICAÇÃO DE DIRETÓRIOS:")
    media_root = Path(settings.MEDIA_ROOT)
    if media_root.exists():
        print(f"   ✓ MEDIA_ROOT existe: {media_root}")
        print(f"   Permissões: {oct(media_root.stat().st_mode)[-3:]}")
    else:
        print(f"   ✗ MEDIA_ROOT NÃO existe: {media_root}")
    print()
    
    # 3. Verificar subdiretório uploads
    uploads_dir = media_root / 'uploads'
    if uploads_dir.exists():
        print(f"   ✓ Diretório uploads existe: {uploads_dir}")
        # Contar imagens
        imagens = list(uploads_dir.glob('*'))
        print(f"   Total de arquivos: {len(imagens)}")
        if imagens:
            print(f"   Exemplos (primeiros 5):")
            for img in imagens[:5]:
                print(f"     - {img.name} ({img.stat().st_size} bytes)")
    else:
        print(f"   ✗ Diretório uploads NÃO existe: {uploads_dir}")
    print()
    
    # 4. Verificar como os caminhos são construídos no código
    print("3. ANÁLISE DE CONSTRUÇÃO DE CAMINHOS:")
    print("   No código atual, os caminhos são construídos como:")
    print(f"   image_path = 'media/uploads/{{filename}}'")
    print(f"   image_url = '{{MEDIA_URL}}uploads/{{filename}}'")
    print()
    
    # 5. Simular construção de caminho
    print("4. SIMULAÇÃO DE RETORNO:")
    exemplo_filename = "exemplo-uuid.jpg"
    image_path_construido = f"media/uploads/{exemplo_filename}"
    image_url_construido = f"{settings.MEDIA_URL}uploads/{exemplo_filename}"
    
    print(f"   image_path retornado: '{image_path_construido}'")
    print(f"   image_url retornado: '{image_url_construido}'")
    print()
    
    # 6. Verificar caminho real no sistema de arquivos
    print("5. MAPEAMENTO REAL:")
    caminho_relativo = image_path_construido
    caminho_absoluto_esperado = media_root / caminho_relativo.replace('media/', '')
    
    print(f"   Caminho relativo (retornado): {caminho_relativo}")
    print(f"   Caminho absoluto esperado: {caminho_absoluto_esperado}")
    if caminho_absoluto_esperado.exists():
        print(f"   ✓ Arquivo existe no sistema de arquivos")
    else:
        print(f"   ✗ Arquivo NÃO existe no sistema de arquivos")
    print()
    
    # 7. Verificar VITRINEZAP_IMAGES_PATH
    print("6. CONFIGURAÇÃO VITRINEZAP:")
    vitrinezap_path = Path('/data/vitrinezap/images')
    print(f"   VITRINEZAP_IMAGES_PATH: {vitrinezap_path}")
    if vitrinezap_path.exists():
        print(f"   ✓ Diretório existe")
        if settings.MEDIA_ROOT == vitrinezap_path:
            print(f"   ✓ MEDIA_ROOT está apontando para este diretório")
        else:
            print(f"   ✗ MEDIA_ROOT NÃO está apontando para este diretório")
            print(f"     MEDIA_ROOT atual: {settings.MEDIA_ROOT}")
    else:
        print(f"   ✗ Diretório NÃO existe")
    print()
    
    # 8. Verificar URLs de acesso
    print("7. URLS DE ACESSO:")
    try:
        current_site = Site.objects.get_current()
        domain = current_site.domain
    except:
        domain = "localhost"
    
    # Tentar obter do request se possível
    host_exemplo = "69.169.102.84:5000"  # Do código
    url_completa = f"http://{host_exemplo}{settings.MEDIA_URL}uploads/{exemplo_filename}"
    print(f"   URL completa exemplo: {url_completa}")
    print()
    
    # 9. Resumo e recomendações
    print("8. RESUMO E DIAGNÓSTICO:")
    print()
    
    problemas = []
    avisos = []
    
    if not media_root.exists():
        problemas.append(f"MEDIA_ROOT não existe: {media_root}")
    
    if not uploads_dir.exists():
        problemas.append(f"Diretório uploads não existe: {uploads_dir}")
    
    # Verificar se o caminho retornado corresponde ao MEDIA_ROOT real
    if str(settings.MEDIA_ROOT) != str(Path(settings.BASE_DIR) / 'media'):
        # MEDIA_ROOT está apontando para /data/vitrinezap/images
        if not image_path_construido.startswith('/data'):
            avisos.append(
                "O image_path retornado usa 'media/uploads/' mas MEDIA_ROOT "
                f"está em '{settings.MEDIA_ROOT}'. "
                "O caminho relativo está correto, mas verifique se o servidor "
                "está servindo arquivos do diretório correto."
            )
    
    if problemas:
        print("   PROBLEMAS ENCONTRADOS:")
        for problema in problemas:
            print(f"   ✗ {problema}")
        print()
    
    if avisos:
        print("   AVISOS:")
        for aviso in avisos:
            print(f"   ⚠ {aviso}")
        print()
    
    if not problemas and not avisos:
        print("   ✓ Configuração parece estar correta!")
    print()
    
    print("=" * 80)
    print("FIM DA VERIFICAÇÃO")
    print("=" * 80)

if __name__ == '__main__':
    verificar_configuracao_imagens()

