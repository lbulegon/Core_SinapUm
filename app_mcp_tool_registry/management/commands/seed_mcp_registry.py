"""
Management command para popular o registry com dados iniciais
"""
from django.core.management.base import BaseCommand
from app_mcp_tool_registry.models import ClientApp, Tool, ToolVersion
import secrets


class Command(BaseCommand):
    help = 'Popula o MCP Tool Registry com dados iniciais'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Iniciando seed do MCP Registry...'))
        
        # 1. Criar ClientApp vitrinezap
        client, created = ClientApp.objects.get_or_create(
            key='vitrinezap',
            defaults={
                'name': 'VitrineZap',
                'is_active': True
            }
        )
        
        if created:
            client.generate_api_key()
            client.save()
            self.stdout.write(self.style.SUCCESS(f'✓ ClientApp "vitrinezap" criado'))
        else:
            self.stdout.write(self.style.WARNING(f'→ ClientApp "vitrinezap" já existe'))
        
        # Gerar API key se não existir
        if not client.api_key:
            client.generate_api_key()
            client.save()
            self.stdout.write(self.style.SUCCESS(f'✓ API key gerada para vitrinezap'))
        
        # 2. Criar Tool vitrinezap.analisar_produto
        tool, created = Tool.objects.get_or_create(
            name='vitrinezap.analisar_produto',
            defaults={
                'description': 'Analisa produto e retorna JSON estruturado',
                'is_active': True
            }
        )
        
        if created:
            self.stdout.write(self.style.SUCCESS(f'✓ Tool "vitrinezap.analisar_produto" criada'))
        else:
            self.stdout.write(self.style.WARNING(f'→ Tool "vitrinezap.analisar_produto" já existe'))
        
        # Adicionar vitrinezap aos allowed_clients
        if client not in tool.allowed_clients.all():
            tool.allowed_clients.add(client)
            self.stdout.write(self.style.SUCCESS(f'✓ Cliente vitrinezap adicionado aos allowed_clients'))
        
        # 3. Criar ToolVersion 1.0.0 - OpenMind analyze-product-image
        from django.conf import settings
        openmind_url = getattr(settings, 'OPENMIND_AI_URL', 'http://openmind:8001')
        tool_version, created = ToolVersion.objects.get_or_create(
            tool=tool,
            version='1.0.0',
            defaults={
                'is_active': True,
                'is_deprecated': False,
                'runtime': 'openmind_http',
                'config': {
                    'url': f'{openmind_url.rstrip("/")}/api/v1/analyze-product-image',
                    'timeout_s': 60
                },
                'input_schema': {
                    'type': 'object',
                    'properties': {
                        'source': {
                            'type': 'string',
                            'enum': ['image', 'text'],
                            'description': 'Fonte dos dados: image ou text'
                        },
                        'text': {
                            'type': 'string',
                            'description': 'Texto do produto (opcional)'
                        },
                        'image_url': {
                            'type': 'string',
                            'description': 'URL da imagem do produto (opcional)'
                        },
                        'image_base64': {
                            'type': 'string',
                            'description': 'Imagem em base64 (opcional)'
                        },
                        'locale': {
                            'type': 'string',
                            'default': 'pt-BR',
                            'description': 'Locale da análise'
                        },
                        'mode': {
                            'type': 'string',
                            'enum': ['fast', 'strict'],
                            'default': 'fast',
                            'description': 'Modo de análise: fast ou strict'
                        },
                        'hints': {
                            'type': 'object',
                            'properties': {
                                'categoria_sugerida': {
                                    'type': 'string'
                                },
                                'marca_sugerida': {
                                    'type': 'string'
                                }
                            },
                            'description': 'Dicas opcionais para a análise'
                        }
                    }
                },
                'output_schema': {
                    'type': 'object',
                    'properties': {
                        'nome': {
                            'type': 'string',
                            'description': 'Nome do produto'
                        },
                        'marca': {
                            'type': 'string',
                            'description': 'Marca do produto'
                        },
                        'categoria': {
                            'type': 'string',
                            'description': 'Categoria do produto'
                        },
                        'descricao': {
                            'type': 'string',
                            'description': 'Descrição do produto'
                        },
                        'preco_sugerido': {
                            'type': 'number',
                            'description': 'Preço sugerido (opcional)'
                        },
                        'atributos': {
                            'type': 'array',
                            'items': {
                                'type': 'object',
                                'properties': {
                                    'key': {'type': 'string'},
                                    'value': {'type': 'string'}
                                }
                            },
                            'description': 'Lista de atributos key/value'
                        },
                        'tags': {
                            'type': 'array',
                            'items': {'type': 'string'},
                            'description': 'Lista de tags'
                        },
                        'confianca': {
                            'type': 'number',
                            'minimum': 0,
                            'maximum': 1,
                            'description': 'Nível de confiança da análise (0-1)'
                        },
                        'warnings': {
                            'type': 'array',
                            'items': {'type': 'string'},
                            'description': 'Lista de avisos'
                        }
                    },
                    'required': ['nome', 'categoria', 'descricao']
                },
                'prompt_ref': 'PROMPT_ANALISE_PRODUTO_V1'
            }
        )
        
        if created:
            self.stdout.write(self.style.SUCCESS(f'✓ ToolVersion 1.0.0 criada'))
        else:
            self.stdout.write(self.style.WARNING(f'→ ToolVersion 1.0.0 já existe'))
        
        # 4. Setar current_version
        if tool.current_version != tool_version:
            tool.current_version = tool_version
            tool.save()
            self.stdout.write(self.style.SUCCESS(f'✓ Versão atual da tool definida como 1.0.0'))
        
        # 5. Criar tool sparkscore.analisar_peca
        sparkscore_url = getattr(settings, 'SPARKSCORE_BASE_URL', 'http://sparkscore_service:8006')
        tool_spark, _ = Tool.objects.get_or_create(
            name='sparkscore.analisar_peca',
            defaults={
                'description': 'Analisa peça criativa (texto, imagem) via SparkScore - orbitais semiótico, emocional, CSV, etc.',
                'is_active': True,
            }
        )
        if client not in tool_spark.allowed_clients.all():
            tool_spark.allowed_clients.add(client)
        ToolVersion.objects.get_or_create(
            tool=tool_spark,
            version='1.0.0',
            defaults={
                'is_active': True,
                'is_deprecated': False,
                'runtime': 'sparkscore',
                'config': {
                    'url': f'{sparkscore_url.rstrip("/")}/api/v1/analyze_piece',
                    'timeout_s': 30,
                },
                'input_schema': {
                    'type': 'object',
                    'properties': {
                        'piece_id': {'type': 'string'},
                        'piece_type': {'type': 'string', 'enum': ['image', 'text', 'video']},
                        'text_overlay': {'type': 'string'},
                        'caption': {'type': 'string'},
                        'objective': {'type': 'object'},
                        'distribution': {'type': 'object'},
                    },
                },
            }
        )
        if not tool_spark.current_version:
            tool_spark.current_version = tool_spark.versions.first()
            tool_spark.save()
        self.stdout.write(self.style.SUCCESS('✓ Tool sparkscore.analisar_peca configurada'))
        
        # 6. Imprimir API key
        self.stdout.write('')
        self.stdout.write(self.style.SUCCESS('=' * 60))
        self.stdout.write(self.style.SUCCESS('API KEY DO VITRINEZAP:'))
        self.stdout.write(self.style.SUCCESS('=' * 60))
        self.stdout.write(self.style.WARNING(client.api_key))
        self.stdout.write(self.style.SUCCESS('=' * 60))
        self.stdout.write('')
        self.stdout.write(self.style.SUCCESS('✓ Seed concluído com sucesso!'))

