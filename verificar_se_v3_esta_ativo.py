#!/usr/bin/env python
import django
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'setup.settings')
django.setup()

from app_mcp_tool_registry.models import Tool
from app_sinapum.models import PromptTemplate

print("="*60)
print("VERIFICAÇÃO DIRETA")
print("="*60)

tool = Tool.objects.get(name='vitrinezap.analisar_produto')
prompt_ref = tool.current_version.prompt_ref

print(f"Prompt Ref na ToolVersion: {prompt_ref}")

prompt = PromptTemplate.objects.filter(nome=prompt_ref, ativo=True).first()

if prompt:
    print(f"Prompt encontrado no banco: {prompt.nome}")
    print(f"Versão do prompt: {prompt.versao}")
    print(f"Ativo: {prompt.ativo}")
    print(f"É padrão: {prompt.eh_padrao}")
    print()
    
    if prompt.versao == '3.0.0':
        print("✅ SIM! O prompt v3 está configurado e ativo!")
        print("   Ele será usado na próxima chamada da tool.")
    else:
        print(f"⚠️ O prompt encontrado é v{prompt.versao}, não v3.0.0")
else:
    print("❌ Prompt não encontrado no banco!")

print("="*60)

