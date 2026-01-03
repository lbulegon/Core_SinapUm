#!/usr/bin/env python
"""
Script para criar prompt de análise de imagens de produtos no banco de dados
"""
import os
import sys
import django

sys.path.insert(0, '/app')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'setup.settings')
django.setup()

from app_sinapum.models import PromptTemplate, Sistema

def create_prompt_analise_imagem():
    """Cria o prompt de análise de imagens de produtos"""
    
    print("="*60)
    print("CRIANDO PROMPT: Análise de Produto por Imagem v1")
    print("="*60)
    
    # Prompt que estava sendo usado como fallback no método legado
    prompt_text = """Analise esta imagem de um produto e extraia TODAS as informações visíveis no rótulo, etiqueta ou embalagem.

Extraia as seguintes informações:
- Nome do produto
- Marca
- Categoria (se visível)
- Código de barras (se visível)
- Descrição/ingredientes (se visível)
- Informações nutricionais (se visível)
- Dimensões da embalagem (se visível)
- Peso/volume (se visível)
- Qualquer outra informação relevante visível na imagem

Retorne os dados em formato JSON estruturado compatível com o modelo ÉVORA.

IMPORTANTE:
- Extraia apenas informações que estão VISÍVEIS na imagem
- NÃO invente ou assuma informações que não estão visíveis
- Se alguma informação não estiver visível, use null ou omita o campo
- Seja específico e detalhado na descrição
- Para categoria, use termos comerciais padrão
- Para subcategoria, seja mais específico"""
    
    # Tentar buscar sistema "evora" ou criar sem sistema (global)
    sistema = None
    try:
        sistema = Sistema.objects.get(codigo='evora', ativo=True)
        print(f"✅ Sistema encontrado: {sistema.codigo}")
    except Sistema.DoesNotExist:
        print("⚠️ Sistema 'evora' não encontrado, criando prompt global (sem sistema)")
        # Tentar outros sistemas
        sistemas = Sistema.objects.filter(ativo=True)
        if sistemas.exists():
            sistema = sistemas.first()
            print(f"   Usando sistema: {sistema.codigo}")
    
    # Criar ou atualizar prompt
    prompt, created = PromptTemplate.objects.get_or_create(
        nome="Análise de Produto por Imagem v1",
        tipo_prompt="analise_produto_imagem_v1",
        sistema=sistema,
        defaults={
            'prompt_text': prompt_text,
            'ativo': True,
            'eh_padrao': True,
            'versao': '1.0.0',
            'descricao': 'Prompt para análise de imagens de produtos usando IA. Extrai informações visíveis do rótulo, etiqueta ou embalagem.',
            'tipo_prompt': 'analise_produto_imagem_v1'
        }
    )
    
    if created:
        print(f"✅ Prompt criado: {prompt.nome}")
        print(f"   Tipo: {prompt.tipo_prompt}")
        print(f"   Sistema: {prompt.sistema.codigo if prompt.sistema else 'Global'}")
        print(f"   Versão: {prompt.versao}")
        print(f"   Tamanho: {len(prompt.prompt_text)} caracteres")
        print(f"   Ativo: {prompt.ativo}")
        print(f"   É Padrão: {prompt.eh_padrao}")
    else:
        # Atualizar prompt existente
        prompt.prompt_text = prompt_text
        prompt.ativo = True
        prompt.eh_padrao = True
        prompt.versao = '1.0.0'
        prompt.descricao = 'Prompt para análise de imagens de produtos usando IA. Extrai informações visíveis do rótulo, etiqueta ou embalagem.'
        prompt.save()
        print(f"🔄 Prompt atualizado: {prompt.nome}")
        print(f"   Tipo: {prompt.tipo_prompt}")
        print(f"   Sistema: {prompt.sistema.codigo if prompt.sistema else 'Global'}")
        print(f"   Versão: {prompt.versao}")
        print(f"   Tamanho: {len(prompt.prompt_text)} caracteres")
        print(f"   Ativo: {prompt.ativo}")
        print(f"   É Padrão: {prompt.eh_padrao}")
    
    print("\n" + "="*60)
    print("✅ Prompt criado/atualizado com sucesso!")
    print("="*60)
    print("\n📝 O prompt agora está disponível para:")
    print("   - MCP Service (via prompt_ref: 'analise_produto_imagem_v1')")
    print("   - Método legado (via get_prompt_from_database)")
    print("="*60)

if __name__ == '__main__':
    create_prompt_analise_imagem()

