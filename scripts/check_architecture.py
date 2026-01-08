#!/usr/bin/env python
"""
Script de Verificação de Arquitetura
=====================================

Verifica se o código está usando arquitetura ANTIGA ou NOVA.
Ajuda a evitar confusão entre código legado e novo código.

Uso:
    python scripts/check_architecture.py
    python scripts/check_architecture.py --file path/to/file.py
    python scripts/check_architecture.py --import app_whatsapp_integration
"""

import os
import sys
import re
from pathlib import Path
from typing import List, Dict, Tuple

# Mapeamento de arquitetura
ARCHITECTURE_MAP = {
    # ANTIGO (Legacy)
    'legacy': {
        'apps': [
            'app_whatsapp_integration',  # Évora
            'app_sinapum.views_evolution',  # Core
            'app_sinapum.evolution_service',  # Core
        ],
        'urls': [
            r'/api/whatsapp/',  # Évora
            r'/whatsapp/api/',  # Core
        ],
        'models': [
            'EvolutionMessage',  # Évora (antigo)
            'WhatsAppMessageLog',  # Évora (antigo)
            'EvolutionInstance',  # Évora (antigo, instância única)
        ],
        'views': [
            'webhook_evolution_api',  # Évora
            'whatsapp_create_instance',  # Core
            'whatsapp_get_qrcode',  # Core
        ],
    },
    # NOVO (Nova Arquitetura)
    'new': {
        'apps': [
            'app_whatsapp_gateway',  # Core
            'app_conversations',  # Core
            'app_ai_bridge',  # Core
            'app_mcp',  # Core
            'app_console',  # Évora
        ],
        'urls': [
            r'/webhooks/evolution/',  # Core
            r'/console/',  # Core/Évora
            r'/ai/',  # Core
            r'/mcp/',  # Core
            r'/channels/whatsapp/',  # Core
            r'/instances/evolution/',  # Core
        ],
        'models': [
            'Conversation',  # Core (novo)
            'Message',  # Core (novo, não EvolutionMessage)
            'Suggestion',  # Core (novo)
        ],
        'views': [
            'webhook_receiver',  # Core (novo)
            'create_instance',  # Core (novo)
            'get_qr',  # Core (novo)
        ],
    }
}


def check_file(file_path: str) -> Dict[str, List[str]]:
    """Verifica um arquivo Python e identifica uso de arquitetura antiga/nova"""
    issues = {
        'legacy_imports': [],
        'new_imports': [],
        'legacy_urls': [],
        'new_urls': [],
        'legacy_models': [],
        'new_models': [],
    }
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            lines = content.split('\n')
    except Exception as e:
        print(f"❌ Erro ao ler arquivo {file_path}: {e}")
        return issues
    
    # Verificar imports
    for i, line in enumerate(lines, 1):
        # Imports
        for legacy_app in ARCHITECTURE_MAP['legacy']['apps']:
            if legacy_app in line and ('import' in line or 'from' in line):
                issues['legacy_imports'].append(f"Linha {i}: {line.strip()}")
        
        for new_app in ARCHITECTURE_MAP['new']['apps']:
            if new_app in line and ('import' in line or 'from' in line):
                issues['new_imports'].append(f"Linha {i}: {line.strip()}")
        
        # URLs
        for legacy_url in ARCHITECTURE_MAP['legacy']['urls']:
            if re.search(legacy_url, line):
                issues['legacy_urls'].append(f"Linha {i}: {line.strip()}")
        
        for new_url in ARCHITECTURE_MAP['new']['urls']:
            if re.search(new_url, line):
                issues['new_urls'].append(f"Linha {i}: {line.strip()}")
        
        # Models
        for legacy_model in ARCHITECTURE_MAP['legacy']['models']:
            if legacy_model in line:
                issues['legacy_models'].append(f"Linha {i}: {line.strip()}")
        
        for new_model in ARCHITECTURE_MAP['new']['models']:
            if new_model in line:
                issues['new_models'].append(f"Linha {i}: {line.strip()}")
    
    return issues


def print_report(file_path: str, issues: Dict[str, List[str]]):
    """Imprime relatório de verificação"""
    print(f"\n{'='*80}")
    print(f"📄 Arquivo: {file_path}")
    print(f"{'='*80}")
    
    # Legacy
    if any(issues[k] for k in ['legacy_imports', 'legacy_urls', 'legacy_models']):
        print("\n🔴 ARQUITETURA ANTIGA (LEGACY) DETECTADA:")
        if issues['legacy_imports']:
            print("  📦 Imports:")
            for item in issues['legacy_imports']:
                print(f"    - {item}")
        if issues['legacy_urls']:
            print("  🔗 URLs:")
            for item in issues['legacy_urls']:
                print(f"    - {item}")
        if issues['legacy_models']:
            print("  🗄️ Models:")
            for item in issues['legacy_models']:
                print(f"    - {item}")
    
    # New
    if any(issues[k] for k in ['new_imports', 'new_urls', 'new_models']):
        print("\n🟢 ARQUITETURA NOVA DETECTADA:")
        if issues['new_imports']:
            print("  📦 Imports:")
            for item in issues['new_imports']:
                print(f"    - {item}")
        if issues['new_urls']:
            print("  🔗 URLs:")
            for item in issues['new_urls']:
                print(f"    - {item}")
        if issues['new_models']:
            print("  🗄️ Models:")
            for item in issues['new_models']:
                print(f"    - {item}")
    
    # Mixed (problema!)
    has_legacy = any(issues[k] for k in ['legacy_imports', 'legacy_urls', 'legacy_models'])
    has_new = any(issues[k] for k in ['new_imports', 'new_urls', 'new_models'])
    
    if has_legacy and has_new:
        print("\n⚠️  ATENÇÃO: Arquitetura MISTA detectada!")
        print("   Este arquivo usa código ANTIGO e NOVO ao mesmo tempo.")
        print("   Revise para evitar confusão.")
    
    if not has_legacy and not has_new:
        print("\n✅ Nenhuma arquitetura WhatsApp detectada (arquivo não relacionado)")


def main():
    """Função principal"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Verifica uso de arquitetura antiga vs nova')
    parser.add_argument('--file', help='Arquivo específico para verificar')
    parser.add_argument('--import', dest='import_name', help='Verificar se import específico é antigo ou novo')
    parser.add_argument('--all', action='store_true', help='Verificar todos os arquivos Python')
    
    args = parser.parse_args()
    
    if args.import_name:
        # Verificar se import é antigo ou novo
        is_legacy = any(args.import_name in app for app in ARCHITECTURE_MAP['legacy']['apps'])
        is_new = any(args.import_name in app for app in ARCHITECTURE_MAP['new']['apps'])
        
        if is_legacy:
            print(f"🔴 {args.import_name} é ARQUITETURA ANTIGA (Legacy)")
        elif is_new:
            print(f"🟢 {args.import_name} é ARQUITETURA NOVA")
        else:
            print(f"❓ {args.import_name} não identificado como antigo ou novo")
        return
    
    if args.file:
        # Verificar arquivo específico
        if not os.path.exists(args.file):
            print(f"❌ Arquivo não encontrado: {args.file}")
            return
        
        issues = check_file(args.file)
        print_report(args.file, issues)
        return
    
    if args.all:
        # Verificar todos os arquivos Python
        base_dir = Path(__file__).parent.parent
        python_files = list(base_dir.rglob('*.py'))
        
        print(f"🔍 Verificando {len(python_files)} arquivos Python...")
        
        for py_file in python_files:
            # Ignorar arquivos de migração e __pycache__
            if 'migrations' in str(py_file) or '__pycache__' in str(py_file):
                continue
            
            issues = check_file(str(py_file))
            if any(issues.values()):
                print_report(str(py_file), issues)
        return
    
    # Modo padrão: mostrar ajuda
    print("""
🔍 Verificador de Arquitetura - Antigo vs Novo

Uso:
    python scripts/check_architecture.py --file path/to/file.py
    python scripts/check_architecture.py --import app_whatsapp_integration
    python scripts/check_architecture.py --all

Exemplos:
    # Verificar um arquivo específico
    python scripts/check_architecture.py --file app_whatsapp_gateway/views.py
    
    # Verificar se um import é antigo ou novo
    python scripts/check_architecture.py --import app_whatsapp_integration
    
    # Verificar todos os arquivos
    python scripts/check_architecture.py --all
    """)


if __name__ == '__main__':
    main()

