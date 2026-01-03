#!/usr/bin/env python
"""
Script para migrar prompt do PostgreSQL para inline no config da ToolVersion
"""
import os
import sys
import django

sys.path.insert(0, '/app')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'setup.settings')
django.setup()

from app_mcp_tool_registry.models import Tool, ToolVersion
from app_sinapum.models import PromptTemplate

def migrar_prompt_para_inline():
    """Migra prompt do PostgreSQL para inline no config"""
    
    print("="*80)
    print("MIGRAÇÃO: Prompt PostgreSQL → Inline Config")
    print("="*80)
    
    # 1. Buscar tool
    try:
        tool = Tool.objects.get(name='vitrinezap.analisar_produto')
        print(f"✅ Tool encontrada: {tool.name}")
    except Tool.DoesNotExist:
        print("❌ Tool 'vitrinezap.analisar_produto' não encontrada")
        return
    
    # 2. Buscar versão atual
    version = tool.current_version
    if not version:
        print("❌ Tool não tem versão atual definida")
        return
    
    print(f"📋 Versão atual: {version.version}")
    print(f"   Prompt Ref: {version.prompt_ref}")
    
    # 3. Buscar prompt do PostgreSQL
    if version.prompt_ref:
        try:
            prompt_template = PromptTemplate.objects.filter(
                nome=version.prompt_ref,
                ativo=True
            ).first()
            
            if not prompt_template:
                # Tentar buscar por tipo_prompt
                prompt_template = PromptTemplate.get_prompt_ativo(
                    version.prompt_ref,
                    sistema=None
                )
            
            if prompt_template:
                prompt_text = prompt_template.get_prompt_text_com_parametros()
                print(f"✅ Prompt encontrado no PostgreSQL:")
                print(f"   Nome: {prompt_template.nome}")
                print(f"   Versão: {prompt_template.versao}")
                print(f"   Tamanho: {len(prompt_text)} caracteres")
            else:
                print(f"⚠️ Prompt '{version.prompt_ref}' não encontrado no PostgreSQL")
                print("   Usando prompt inline do config se existir...")
                if version.config and version.config.get('prompt_inline'):
                    prompt_text = version.config['prompt_inline']
                    print(f"✅ Prompt inline encontrado no config ({len(prompt_text)} caracteres)")
                else:
                    print("❌ Nenhum prompt encontrado!")
                    return
        except Exception as e:
            print(f"❌ Erro ao buscar prompt: {e}")
            return
    else:
        # Verificar se já tem prompt inline
        if version.config and version.config.get('prompt_inline'):
            prompt_text = version.config['prompt_inline']
            print(f"✅ Prompt já está inline no config ({len(prompt_text)} caracteres)")
            print("   Nada a fazer!")
            return
        else:
            print("❌ Nenhum prompt encontrado (nem prompt_ref nem prompt_inline)")
            return
    
    # 4. Atualizar config com prompt inline
    print("\n" + "="*80)
    print("ATUALIZANDO CONFIG...")
    print("="*80)
    
    # Garantir que config existe
    if not version.config:
        version.config = {}
    
    # Adicionar prompt inline (prioridade sobre prompt_ref)
    version.config['prompt_inline'] = prompt_text
    
    # Manter prompt_ref para referência (opcional)
    # version.prompt_ref = None  # Descomentar se quiser remover completamente
    
    version.save()
    
    print("✅ Config atualizado com sucesso!")
    print(f"   Prompt inline adicionado: {len(prompt_text)} caracteres")
    print(f"   Prompt ref mantido: {version.prompt_ref}")
    
    # 5. Verificar resolução
    print("\n" + "="*80)
    print("VERIFICANDO RESOLUÇÃO...")
    print("="*80)
    
    from app_mcp_tool_registry.utils import resolve_prompt_from_ref
    
    # Testar resolução (deve priorizar prompt_inline)
    resolved = resolve_prompt_from_ref(version.prompt_ref, config=version.config)
    if resolved:
        print("✅ Prompt resolvido com sucesso!")
        print(f"   Tamanho: {len(resolved)} caracteres")
        if resolved == prompt_text:
            print("   ✅ Prompt resolvido é o mesmo do inline (correto!)")
        else:
            print("   ⚠️ Prompt resolvido é diferente do inline")
    else:
        print("❌ Erro ao resolver prompt")
    
    print("\n" + "="*80)
    print("✅ MIGRAÇÃO CONCLUÍDA!")
    print("="*80)
    print("\n📝 Próximos passos:")
    print("   1. Teste a tool para verificar se funciona corretamente")
    print("   2. Se funcionar, você pode remover o prompt_ref (opcional)")
    print("   3. Considere mover o prompt para um arquivo separado")
    print("   4. Versionar o prompt no Git")
    print("="*80)

if __name__ == '__main__':
    migrar_prompt_para_inline()

