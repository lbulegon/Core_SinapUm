#!/usr/bin/env python
import django
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'setup.settings')
django.setup()

from app_sinapum.models import PromptTemplate

print("="*80)
print("VERIFICAÇÃO E ATUALIZAÇÃO DE PROMPTS")
print("="*80)

# Listar todos os prompts ativos
prompts = PromptTemplate.objects.filter(
    tipo_prompt='analise_imagem_produto',
    ativo=True
).order_by('-versao')

print(f"\n📋 Prompts ativos encontrados: {prompts.count()}")
for p in prompts:
    status = "⭐ PADRÃO" if p.eh_padrao else ""
    print(f"  • {p.nome} (v{p.versao}) {status} - Sistema: {p.sistema.codigo if p.sistema else 'Global'}")

# Verificar se há múltiplos padrões
padroes = prompts.filter(eh_padrao=True)
print(f"\n⚠️ Prompts marcados como PADRÃO: {padroes.count()}")

if padroes.count() > 1:
    print("   ⚠️ PROBLEMA: Múltiplos prompts padrão podem causar conflito!")
    print("   Desmarcando todos exceto o mais recente...")
    
    # Manter apenas o mais recente como padrão
    mais_recente = padroes.order_by('-versao').first()
    for p in padroes.exclude(id=mais_recente.id):
        p.eh_padrao = False
        p.save()
        print(f"   ✓ Desmarcado: {p.nome} (v{p.versao})")
    
    print(f"   ✅ Mantido como padrão: {mais_recente.nome} (v{mais_recente.versao})")

# Garantir que o v4 é o padrão
v4 = PromptTemplate.objects.filter(
    nome='Análise de Produto - Ultra Específico v4',
    ativo=True
).first()

if v4:
    v4.eh_padrao = True
    v4.sistema = None  # Garantir que é global
    v4.save()
    print(f"\n✅ Prompt v4 configurado como padrão e global")

# Verificar prompt padrão final
padrao_final = PromptTemplate.objects.filter(
    tipo_prompt='analise_imagem_produto',
    ativo=True,
    eh_padrao=True,
    sistema__isnull=True
).first()

if padrao_final:
    print(f"\n✅ Prompt padrão final: {padrao_final.nome} (v{padrao_final.versao})")
else:
    print("\n❌ Nenhum prompt padrão global encontrado!")

print("="*80)

