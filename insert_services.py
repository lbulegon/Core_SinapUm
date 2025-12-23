#!/usr/bin/env python
"""Script para inserir serviços na tabela ServicoExterno"""
import os
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'setup.settings')
django.setup()

from app_sinapum.models import ServicoExterno
from django.conf import settings

def insert_services():
    """Insere todos os serviços encontrados na tabela"""
    
    services = []
    
    # 1. PostgreSQL Database
    postgres, created = ServicoExterno.objects.get_or_create(
        nome="PostgreSQL MCP SinapUm",
        tipo_servico="outro",
        ambiente="producao",
        defaults={
            'url_base': 'postgresql://db:5432',
            'usuario': os.environ.get('POSTGRES_USER', 'mcp_user'),
            'senha': os.environ.get('POSTGRES_PASSWORD', 'mcp_password_change_me'),
            'credenciais_adicionais': {
                'database': os.environ.get('POSTGRES_DB', 'mcp_sinapum'),
                'host': os.environ.get('POSTGRES_HOST', 'db'),
                'port': os.environ.get('POSTGRES_PORT', '5432'),
                'connection_string': os.environ.get('DATABASE_URL', '')
            },
            'observacoes': 'Banco de dados PostgreSQL do MCP SinapUm, rodando em container Docker',
            'ativo': True
        }
    )
    services.append(('PostgreSQL', created))
    
    # 2. OpenMind AI Server (Local)
    openmind_ai, created = ServicoExterno.objects.get_or_create(
        nome="OpenMind AI Server",
        tipo_servico="outro",
        ambiente="producao",
        defaults={
            'url_base': getattr(settings, 'OPENMIND_AI_URL', 'http://127.0.0.1:8000'),
            'api_key': getattr(settings, 'OPENMIND_AI_KEY', ''),
            'credenciais_adicionais': {
                'host': '127.0.0.1',
                'port': '8000',
                'external_url': 'http://69.169.102.84:8000',
                'framework': 'FastAPI',
                'server': 'Uvicorn'
            },
            'observacoes': 'Servidor OpenMind AI local para análise de imagens de produtos',
            'ativo': True
        }
    )
    services.append(('OpenMind AI Server', created))
    
    # 3. OpenMind.org API
    openmind_org, created = ServicoExterno.objects.get_or_create(
        nome="OpenMind.org API",
        tipo_servico="openai",
        ambiente="producao",
        defaults={
            'url_base': getattr(settings, 'OPENMIND_ORG_BASE_URL', 'https://api.openmind.org/api/core/openai'),
            'api_key': getattr(settings, 'OPENMIND_AI_KEY', ''),
            'credenciais_adicionais': {
                'model': getattr(settings, 'OPENMIND_ORG_MODEL', 'gpt-4o'),
                'description': 'API unificada para múltiplos LLMs (OpenAI, Anthropic, Gemini, etc.)',
                'available_models': ['gpt-4o', 'gpt-4-turbo', 'claude-3-opus', 'gemini-pro']
            },
            'observacoes': 'OpenMind.org oferece acesso a múltiplos modelos de IA através de uma API unificada',
            'ativo': True
        }
    )
    services.append(('OpenMind.org API', created))
    
    # 4. Servidor VPS (InterServer)
    vps, created = ServicoExterno.objects.get_or_create(
        nome="Servidor VPS Principal",
        tipo_servico="interserver",
        ambiente="producao",
        defaults={
            'ip_servidor': '69.169.102.84',
            'sistema_operacional': 'Ubuntu (Linux 6.8.0-88-generic)',
            'porta_ssh': 22,
            'credenciais_adicionais': {
                'hostname': 'sinapum',
                'internal_ips': ['172.18.0.1', '172.17.0.1', '172.19.0.1', '172.20.0.1'],
                'services': [
                    'MCP SinapUm (Django - Port 5000)',
                    'OpenMind AI (FastAPI - Port 8000)',
                    'PostgreSQL (Port 5432)'
                ]
            },
            'observacoes': 'Servidor VPS principal onde rodam os serviços MCP SinapUm, OpenMind AI e PostgreSQL',
            'ativo': True
        }
    )
    services.append(('Servidor VPS', created))
    
    # 5. MCP SinapUm Django Application
    mcp_sinapum, created = ServicoExterno.objects.get_or_create(
        nome="MCP SinapUm Django",
        tipo_servico="outro",
        ambiente="producao",
        defaults={
            'url_base': 'http://69.169.102.84:5000',
            'credenciais_adicionais': {
                'port': '5000',
                'framework': 'Django',
                'wsgi_server': 'Gunicorn',
                'admin_url': 'http://69.169.102.84:5000/admin/',
                'api_endpoints': [
                    '/api/v1/analyze-product-image',
                    '/analyze/',
                    '/admin/'
                ]
            },
            'observacoes': 'Aplicação Django principal do MCP SinapUm, servindo na porta 5000',
            'ativo': True
        }
    )
    services.append(('MCP SinapUm Django', created))
    
    # Mostrar resultados
    print("\n" + "="*60)
    print("SERVIÇOS INSERIDOS/ATUALIZADOS")
    print("="*60)
    for nome, criado in services:
        status = "✅ Criado" if criado else "🔄 Atualizado"
        print(f"{status}: {nome}")
    
    print("\n" + "="*60)
    print(f"Total de serviços cadastrados: {ServicoExterno.objects.count()}")
    print("="*60)
    
    # Listar todos os serviços
    print("\n📋 Lista completa de serviços:")
    for servico in ServicoExterno.objects.all().order_by('tipo_servico', 'nome'):
        status = "✓" if servico.ativo else "✗"
        print(f"  {status} {servico.get_tipo_servico_display()} - {servico.nome} ({servico.get_ambiente_display()})")

if __name__ == '__main__':
    insert_services()

