#!/usr/bin/env python
import django
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'setup.settings')
django.setup()

from app_sinapum.models import PromptTemplate
from django.conf import settings

print("="*80)
print("VERIFICAÇÃO: Prompt usado por /analyze/")
print("="*80)

# Simular o que a view analyze_image() faz (com fallback para global)
sistema_codigo = getattr(settings, 'SISTEMA_CODIGO', 'evora')
print(f"Sistema buscado: {sistema_codigo}")

prompt = PromptTemplate.get_prompt_ativo('analise_imagem_produto', sistema=sistema_codigo)

# Se não encontrou no sistema específico, tentar buscar global (sem sistema)
if not prompt:
    print(f"Prompt não encontrado no sistema '{sistema_codigo}', tentando buscar globalmente...")
    prompt = PromptTemplate.get_prompt_ativo('analise_imagem_produto', sistema=None)

if prompt:
    print(f"\n✅ Prompt encontrado:")
    print(f"   Nome: {prompt.nome}")
    print(f"   Versão: {prompt.versao}")
    print(f"   Sistema: {prompt.sistema.codigo if prompt.sistema else 'Global'}")
    print(f"   Ativo: {prompt.ativo}")
    print(f"   É padrão: {prompt.eh_padrao}")
    
    if prompt.versao == '3.0.0':
        print("\n✅ SIM! O prompt v3 está sendo usado pelo /analyze/!")
    else:
        print(f"\n⚠️ NÃO é o v3. Está usando v{prompt.versao}")
        print("   O endpoint /analyze/ NÃO está usando o prompt v3")
else:
    print("\n❌ Nenhum prompt encontrado")
    print("   O endpoint /analyze/ usará o prompt fallback (genérico)")

print("\n" + "="*80)
print("IMPORTANTE:")
print("="*80)
print("O endpoint /analyze/ usa o método LEGADO (analyze_image_with_openmind)")
print("que busca o prompt do PostgreSQL diretamente.")
print()
print("Ele NÃO usa o MCP Service, então não usa a tool vitrinezap.analisar_produto")
print("com o prompt v3 configurado na ToolVersion.")
print("="*80)

