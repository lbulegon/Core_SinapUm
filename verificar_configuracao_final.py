#!/usr/bin/env python
"""
Script para verificar se tudo está configurado corretamente
"""
import django
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'setup.settings')
django.setup()

from app_mcp_tool_registry.models import Tool, ToolVersion
from app_mcp_tool_registry.utils import resolve_prompt_from_ref
from app_sinapum.models import PromptTemplate

print("="*80)
print("VERIFICAÇÃO FINAL DA CONFIGURAÇÃO")
print("="*80)

# 1. Verificar Tool
try:
    tool = Tool.objects.get(name='vitrinezap.analisar_produto')
    print(f"✅ Tool encontrada: {tool.name}")
except Tool.DoesNotExist:
    print("❌ Tool 'vitrinezap.analisar_produto' não encontrada")
    exit(1)

# 2. Verificar Versão
version = tool.current_version
if not version:
    print("❌ Tool não tem versão atual definida")
    exit(1)

print(f"✅ Versão atual: {version.version}")
print(f"   Runtime: {version.runtime}")
print(f"   Prompt Ref: {version.prompt_ref}")
print(f"   Config URL: {version.config.get('url', 'N/A') if version.config else 'N/A'}")

# 3. Verificar Prompt
print("\n" + "-"*80)
print("VERIFICANDO PROMPT...")
print("-"*80)

prompt_text = resolve_prompt_from_ref(version.prompt_ref, config=version.config)
if prompt_text:
    print(f"✅ Prompt resolvido com sucesso!")
    print(f"   Tamanho: {len(prompt_text)} caracteres")
    print(f"   Primeiros 200 chars: {prompt_text[:200]}...")
    
    # Verificar se é o prompt melhorado
    if "Extração Detalhada" in prompt_text or "EXTREMA ATENÇÃO" in prompt_text:
        print("   ✅ É o prompt melhorado (Extração Detalhada)")
    else:
        print("   ⚠️ Pode não ser o prompt melhorado")
else:
    print("❌ Erro ao resolver prompt")
    exit(1)

# 4. Listar prompts disponíveis
print("\n" + "-"*80)
print("PROMPTS DISPONÍVEIS:")
print("-"*80)
prompts = PromptTemplate.objects.filter(
    tipo_prompt='analise_imagem_produto',
    ativo=True
).order_by('-versao')

for p in prompts:
    status = "⭐ PADRÃO" if p.eh_padrao else ""
    print(f"  • {p.nome} (v{p.versao}) {status}")

# 5. Verificar se o prompt usado está na lista
prompt_usado = PromptTemplate.objects.filter(
    nome=version.prompt_ref,
    ativo=True
).first()

if prompt_usado:
    print(f"\n✅ Prompt usado está ativo: {prompt_usado.nome} (v{prompt_usado.versao})")
    if prompt_usado.parametros:
        temp = prompt_usado.parametros.get('temperature', 'N/A')
        print(f"   Temperature: {temp}")
else:
    print(f"\n⚠️ Prompt '{version.prompt_ref}' não encontrado ou inativo")

# 6. Resumo final
print("\n" + "="*80)
print("RESUMO FINAL")
print("="*80)
print("✅ Tool configurada")
print("✅ Versão ativa")
print("✅ Prompt resolvido")
print("✅ Pronto para uso!")
print("\n📝 Próximos passos:")
print("   1. Teste com uma imagem real")
print("   2. Verifique se a extração melhorou")
print("   3. Ajuste o prompt se necessário")
print("="*80)

