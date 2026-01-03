#!/usr/bin/env python
import django
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'setup.settings')
django.setup()

from app_sinapum.models import PromptTemplate
from app_mcp_tool_registry.utils import resolve_prompt_from_ref

# Verificar prompt pelo nome
prompt = PromptTemplate.objects.filter(nome='Análise de Produto por Imagem - modelo.json Completo', ativo=True).first()
if prompt:
    print('✅ Prompt encontrado pelo nome!')
    print(f'ID: {prompt.id}')
    print(f'Nome: {prompt.nome}')
    print(f'Versão: {prompt.versao}')
    print(f'Tipo: {prompt.tipo_prompt}')
    print(f'Sistema: {prompt.sistema.codigo if prompt.sistema else "Global"}')
    print(f'Texto (primeiros 300 chars): {prompt.prompt_text[:300]}...')
    print()
    
    # Testar resolução via resolve_prompt_from_ref
    print('Testando resolução via resolve_prompt_from_ref...')
    prompt_text = resolve_prompt_from_ref('Análise de Produto por Imagem - modelo.json Completo')
    if prompt_text:
        print('✅ Prompt resolvido com sucesso via resolve_prompt_from_ref!')
        print(f'Tamanho: {len(prompt_text)} caracteres')
    else:
        print('❌ Prompt NÃO foi resolvido via resolve_prompt_from_ref')
        print('   Isso significa que precisa ajustar a busca no utils.py')
else:
    print('❌ Prompt não encontrado')

