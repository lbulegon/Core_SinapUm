#!/usr/bin/env python
"""
Script para testar se o prompt_info está sendo incluído no cadastro_meta
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'setup.settings')
django.setup()

from app_sinapum.models import PromptTemplate

# Verificar qual prompt está ativo
prompt = PromptTemplate.objects.filter(
    tipo_prompt='analise_imagem_produto',
    ativo=True,
    eh_padrao=True
).order_by('-versao').first()

if prompt:
    print(f"✅ Prompt ativo encontrado:")
    print(f"   Nome: {prompt.nome}")
    print(f"   Versão: {prompt.versao}")
    print(f"   Sistema: {prompt.sistema.codigo if prompt.sistema else 'Global'}")
    print(f"   Fonte: PostgreSQL")
    print(f"   Tipo: {prompt.tipo_prompt}")
    print(f"   Parâmetros: {prompt.parametros if hasattr(prompt, 'parametros') and prompt.parametros else {}}")
    
    # Simular o prompt_info que seria criado
    prompt_info = {
        'nome': prompt.nome,
        'versao': prompt.versao,
        'fonte': 'PostgreSQL',
        'sistema': prompt.sistema.codigo if prompt.sistema else 'Global',
        'tipo_prompt': prompt.tipo_prompt,
        'parametros': prompt.parametros if hasattr(prompt, 'parametros') and prompt.parametros else {}
    }
    
    print(f"\n📋 prompt_info que seria criado:")
    import json
    print(json.dumps(prompt_info, indent=2, ensure_ascii=False))
    
    print(f"\n📦 Exemplo de cadastro_meta com prompt_usado:")
    cadastro_meta_exemplo = {
        "capturado_por": "VitrineZap (IA Évora)",
        "data_captura": "2025-12-26T12:00:00Z",
        "fonte": "Análise automática de imagem: media/uploads/test.jpg",
        "confianca_da_leitura": 0.95,
        "detalhes_rotulo": {
            "frase": None,
            "origem": None,
            "duracao": None
        },
        "prompt_usado": prompt_info
    }
    print(json.dumps(cadastro_meta_exemplo, indent=2, ensure_ascii=False))
else:
    print("❌ Nenhum prompt ativo encontrado!")

