#!/usr/bin/env python
"""
Script para registrar a tool MCP de análise de imagens de produtos (VitrineZap)
"""
import os
import sys
import django

sys.path.insert(0, '/app')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'setup.settings')
django.setup()

from app_mcp_tool_registry.models import ClientApp, Tool, ToolVersion
from django.conf import settings
import json

def register_vitrinezap_tool():
    """Registra a tool vitrinezap.analisar_produto no MCP Registry"""
    
    print("="*60)
    print("REGISTRANDO TOOL MCP: vitrinezap.analisar_produto")
    print("="*60)
    
    # 1. Criar ou obter ClientApp "vitrinezap"
    client_app, created = ClientApp.objects.get_or_create(
        key="vitrinezap",
        defaults={
            'name': 'VitrineZap - Sistema de Análise de Produtos',
            'is_active': True
        }
    )
    
    if created:
        client_app.generate_api_key()
        client_app.save()
        print(f"✅ ClientApp criado: {client_app.key}")
        print(f"   API Key: {client_app.api_key}")
    else:
        print(f"🔄 ClientApp já existe: {client_app.key}")
        if not client_app.api_key:
            client_app.generate_api_key()
            client_app.save()
            print(f"   Nova API Key gerada: {client_app.api_key}")
    
    # 2. Criar ou obter Tool
    tool, created = Tool.objects.get_or_create(
        name="vitrinezap.analisar_produto",
        defaults={
            'description': 'Analisa imagens de produtos e extrai informações estruturadas (nome, marca, categoria, características, etc.)',
            'is_active': True
        }
    )
    
    if created:
        print(f"✅ Tool criada: {tool.name}")
    else:
        print(f"🔄 Tool já existe: {tool.name}")
    
    # Associar ClientApp à Tool
    tool.allowed_clients.add(client_app)
    
    # 3. Criar ToolVersion 1.0.0
    openmind_url = getattr(settings, 'OPENMIND_AI_URL', 'http://openmind:8001')
    
    # Input Schema - JSON Schema para validação
    input_schema = {
        "type": "object",
        "required": ["image"],
        "properties": {
            "image": {
                "oneOf": [
                    {
                        "type": "string",
                        "format": "uri",
                        "description": "URL da imagem a ser analisada"
                    },
                    {
                        "type": "string",
                        "format": "binary",
                        "description": "Imagem em base64"
                    }
                ],
                "description": "Imagem do produto a ser analisada (URL ou base64)"
            },
            "image_url": {
                "type": "string",
                "format": "uri",
                "description": "URL da imagem (alternativa a 'image')"
            },
            "prompt": {
                "type": "string",
                "description": "Prompt customizado para análise (opcional)"
            },
            "prompt_params": {
                "type": "object",
                "description": "Parâmetros adicionais para o prompt (opcional)"
            }
        }
    }
    
    # Output Schema - JSON Schema para validação
    output_schema = {
        "type": "object",
        "properties": {
            "success": {
                "type": "boolean",
                "description": "Indica se a análise foi bem-sucedida"
            },
            "data": {
                "type": "object",
                "description": "Dados extraídos do produto",
                "properties": {
                    "produto": {
                        "type": "object",
                        "description": "Informações do produto"
                    },
                    "produto_generico_catalogo": {
                        "type": "object",
                        "description": "Informações genéricas do catálogo"
                    },
                    "produto_viagem": {
                        "type": "object",
                        "description": "Informações da viagem de compras"
                    }
                }
            },
            "image_path": {
                "type": "string",
                "description": "Caminho relativo da imagem salva"
            },
            "image_url": {
                "type": "string",
                "format": "uri",
                "description": "URL completa da imagem salva"
            },
            "saved_filename": {
                "type": "string",
                "description": "Nome do arquivo salvo"
            },
            "error": {
                "type": "string",
                "description": "Mensagem de erro (se houver)"
            },
            "error_code": {
                "type": "string",
                "description": "Código do erro (se houver)"
            }
        }
    }
    
    # Config do runtime - OpenMind HTTP
    runtime_config = {
        "url": f"{openmind_url.rstrip('/')}/api/v1/analyze-product-image",
        "method": "POST",
        "timeout_s": 60,
        "headers": {
            "Authorization": "Bearer ${OPENMIND_AI_KEY}"
        }
    }
    
    # Criar versão 1.0.0
    version, created = ToolVersion.objects.get_or_create(
        tool=tool,
        version="1.0.0",
        defaults={
            'is_active': True,
            'is_deprecated': False,
            'input_schema': input_schema,
            'output_schema': output_schema,
            'runtime': 'openmind_http',
            'config': runtime_config,
            'prompt_ref': 'analise_produto_imagem_v1'  # Referência ao prompt template
        }
    )
    
    if created:
        print(f"✅ ToolVersion criada: {tool.name}@1.0.0")
    else:
        print(f"🔄 ToolVersion já existe: {tool.name}@1.0.0")
        # Atualizar se necessário
        version.input_schema = input_schema
        version.output_schema = output_schema
        version.runtime = 'openmind_http'
        version.config = runtime_config
        version.prompt_ref = 'analise_produto_imagem_v1'
        version.is_active = True
        version.is_deprecated = False
        version.save()
        print(f"   ✅ ToolVersion atualizada")
    
    # Definir como current_version se não houver
    if not tool.current_version:
        tool.current_version = version
        tool.save()
        print(f"   ✅ Versão 1.0.0 definida como current_version")
    
    print("\n" + "="*60)
    print("RESUMO")
    print("="*60)
    print(f"ClientApp: {client_app.key} ({client_app.name})")
    print(f"  API Key: {client_app.api_key}")
    print(f"Tool: {tool.name}")
    print(f"  Description: {tool.description}")
    print(f"  Current Version: {tool.current_version.version if tool.current_version else 'N/A'}")
    print(f"  Runtime: {version.runtime}")
    print(f"  Config URL: {runtime_config['url']}")
    print("\n" + "="*60)
    print("✅ Tool registrada com sucesso!")
    print("="*60)
    print("\n📝 Para usar a tool, faça uma requisição para:")
    print(f"   POST http://69.169.102.84:7010/mcp/call")
    print(f"   Headers: X-SINAPUM-KEY: {client_app.api_key}")
    print(f"   Body: {{")
    print(f"     \"tool\": \"vitrinezap.analisar_produto\",")
    print(f"     \"input\": {{")
    print(f"       \"image_url\": \"https://example.com/produto.jpg\"")
    print(f"     }}")
    print(f"   }}")
    print("="*60)

if __name__ == '__main__':
    register_vitrinezap_tool()

