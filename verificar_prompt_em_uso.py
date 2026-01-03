#!/usr/bin/env python
"""
Script para verificar se o prompt v3 está sendo usado
"""
import django
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'setup.settings')
django.setup()

from app_mcp_tool_registry.models import Tool, ToolVersion
from app_mcp_tool_registry.utils import resolve_prompt_from_ref

print("="*80)
print("VERIFICAÇÃO: Prompt v3 em Uso")
print("="*80)

# 1. Verificar ToolVersion
tool = Tool.objects.get(name='vitrinezap.analisar_produto')
version = tool.current_version

print(f"Tool: {tool.name}")
print(f"Versão: {version.version}")
print(f"Prompt Ref Configurado: {version.prompt_ref}")
print()

# 2. Resolver prompt
prompt_text = resolve_prompt_from_ref(version.prompt_ref, config=version.config)

if prompt_text:
    print("✅ Prompt está sendo resolvido corretamente!")
    print(f"   Tamanho: {len(prompt_text)} caracteres")
    print()
    
    # Verificar se é v3
    is_v3 = False
    checks = []
    
    if "Máxima Precisão v3" in prompt_text:
        is_v3 = True
        checks.append("✓ Contém 'Máxima Precisão v3'")
    
    if "NUNCA use" in prompt_text and "Produto não identificado" in prompt_text:
        checks.append("✓ Contém proibição de valores genéricos")
    
    if "4KG" in prompt_text or "peso" in prompt_text.lower():
        checks.append("✓ Contém instruções sobre peso")
    
    if "Checklist" in prompt_text or "CHECKLIST" in prompt_text:
        checks.append("✓ Contém checklist")
    
    if "Temperature: 0.1" in prompt_text or "temperature.*0.1" in prompt_text.lower():
        checks.append("✓ Menciona temperature 0.1")
    
    print(f"   Versão identificada: {'v3.0.0 ✅' if is_v3 else 'Verificando...'}")
    print()
    print("   Verificações:")
    for check in checks:
        print(f"      {check}")
    
    print()
    print("   Primeiros 200 chars do prompt:")
    print(f"   {prompt_text[:200]}...")
    
    if is_v3 and len(checks) >= 3:
        print()
        print("="*80)
        print("✅ CONFIRMADO: Prompt v3 está sendo usado!")
        print("="*80)
    else:
        print()
        print("="*80)
        print("⚠️ ATENÇÃO: Pode não ser o prompt v3 completo")
        print("="*80)
else:
    print("❌ Erro ao resolver prompt")
    print("="*80)

