#!/usr/bin/env python
import os
import sys
import django

sys.path.insert(0, '/app')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'setup.settings')
django.setup()

from app_sinapum.models import ServicoExterno
from django.conf import settings

services_data = [
    {
        'nome': 'PostgreSQL MCP SinapUm',
        'tipo_servico': 'outro',
        'ambiente': 'producao',
        'url_base': 'postgresql://db:5432',
        'usuario': 'mcp_user',
        'senha': 'mcp_password_change_me',
        'credenciais_adicionais': {'database': 'mcp_sinapum', 'host': 'db', 'port': '5432'},
        'observacoes': 'Banco de dados PostgreSQL do MCP SinapUm, rodando em container Docker'
    },
    {
        'nome': 'OpenMind AI Server',
        'tipo_servico': 'outro',
        'ambiente': 'producao',
        'url_base': 'http://127.0.0.1:8000',
        'api_key': getattr(settings, 'OPENMIND_AI_KEY', ''),
        'credenciais_adicionais': {'port': '8000', 'external_url': 'http://69.169.102.84:8000', 'framework': 'FastAPI'},
        'observacoes': 'Servidor OpenMind AI local para análise de imagens de produtos'
    },
    {
        'nome': 'OpenMind.org API',
        'tipo_servico': 'openai',
        'ambiente': 'producao',
        'url_base': 'https://api.openmind.org/api/core/openai',
        'api_key': getattr(settings, 'OPENMIND_AI_KEY', ''),
        'credenciais_adicionais': {'model': 'gpt-4o', 'description': 'API unificada para múltiplos LLMs'},
        'observacoes': 'OpenMind.org oferece acesso a múltiplos modelos de IA através de uma API unificada'
    },
    {
        'nome': 'Servidor VPS Principal',
        'tipo_servico': 'interserver',
        'ambiente': 'producao',
        'ip_servidor': '69.169.102.84',
        'sistema_operacional': 'Ubuntu (Linux 6.8.0-88-generic)',
        'porta_ssh': 22,
        'credenciais_adicionais': {'hostname': 'sinapum', 'services': ['MCP SinapUm (Port 5000)', 'OpenMind AI (Port 8000)', 'PostgreSQL (Port 5432)']},
        'observacoes': 'Servidor VPS principal onde rodam os serviços MCP SinapUm, OpenMind AI e PostgreSQL'
    },
    {
        'nome': 'MCP SinapUm Django',
        'tipo_servico': 'outro',
        'ambiente': 'producao',
        'url_base': 'http://69.169.102.84:5000',
        'credenciais_adicionais': {'port': '5000', 'framework': 'Django', 'wsgi_server': 'Gunicorn', 'admin_url': 'http://69.169.102.84:5000/admin/'},
        'observacoes': 'Aplicação Django principal do MCP SinapUm, servindo na porta 5000'
    }
]

print("="*60)
print("INSERINDO SERVIÇOS NA TABELA ServicoExterno")
print("="*60)

for data in services_data:
    nome = data.pop('nome')
    tipo = data.pop('tipo_servico')
    ambiente = data.pop('ambiente')
    defaults = {**data, 'ativo': True}
    
    servico, created = ServicoExterno.objects.get_or_create(
        nome=nome,
        tipo_servico=tipo,
        ambiente=ambiente,
        defaults=defaults
    )
    status = "✅ Criado" if created else "🔄 Atualizado"
    print(f"{status}: {nome}")

print("\n" + "="*60)
print(f"Total de serviços cadastrados: {ServicoExterno.objects.count()}")
print("="*60)

