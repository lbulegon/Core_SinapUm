"""
Management command para diagnóstico de integrações WhatsApp
===========================================================

Verifica o estado das integrações WhatsApp no Core_SinapUm / VitrineZap,
garantindo que o sistema pode operar em SHADOW MODE sem quebrar nada.

Regra máxima:
- NÃO altera comportamento existente
- NÃO envia mensagens reais
- NÃO intercepta webhooks
- Apenas LÊ, VALIDA e REPORTA

Uso:
    python manage.py whatsapp_diagnose
"""
import os
from datetime import datetime, timedelta
from django.core.management.base import BaseCommand
from django.conf import settings
from django.db import connection
from django.urls import get_resolver
from django.core.exceptions import ImproperlyConfigured

# Imports condicionais (não quebrar se módulos não existirem)
try:
    from core.services.whatsapp.gateway import get_whatsapp_gateway
    from core.services.whatsapp.settings import (
        get_whatsapp_provider,
        is_whatsapp_send_enabled,
        is_whatsapp_shadow_mode,
        get_enabled_shoppers
    )
    WHATSAPP_GATEWAY_AVAILABLE = True
except ImportError:
    WHATSAPP_GATEWAY_AVAILABLE = False

try:
    from core.services.whatsapp.canonical.publisher import get_event_publisher
    CANONICAL_PUBLISHER_AVAILABLE = True
except ImportError:
    CANONICAL_PUBLISHER_AVAILABLE = False

try:
    from app_whatsapp_events.models import WhatsAppEventLog, WhatsAppConversation
    WHATSAPP_EVENTS_AVAILABLE = True
except ImportError:
    WHATSAPP_EVENTS_AVAILABLE = False

try:
    from core.services.whatsapp.canonical.models import CanonicalEventLog
    CANONICAL_EVENTS_AVAILABLE = True
except ImportError:
    CANONICAL_EVENTS_AVAILABLE = False

try:
    from core.services.whatsapp.models import SimulatedMessage
    SIMULATED_MESSAGES_AVAILABLE = True
except ImportError:
    SIMULATED_MESSAGES_AVAILABLE = False


class Command(BaseCommand):
    help = 'Diagnóstico de integrações WhatsApp (modo shadow - apenas leitura)'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.status_ok = []
        self.status_warn = []
        self.status_fail = []
        self.recommendations = []

    def add_arguments(self, parser):
        parser.add_argument(
            '--verbose',
            action='store_true',
            help='Mostra informações detalhadas',
        )

    def handle(self, *args, **options):
        verbose = options.get('verbose', False)
        
        # Cabeçalho
        self.print_header()
        
        # Seções de diagnóstico
        self.check_environment_variables(verbose)
        self.check_provider(verbose)
        self.check_shadow_mode(verbose)
        self.check_webhook_endpoints(verbose)
        self.check_database(verbose)
        self.check_simulator(verbose)
        
        # Resumo final
        self.print_summary()
        
        # Linha final
        self.stdout.write(
            self.style.SUCCESS(
                '\n✓ Diagnóstico concluído — nenhuma ação executada'
            )
        )

    def print_header(self):
        """Imprime cabeçalho com timestamp e ambiente"""
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        environment = getattr(settings, 'ENVIRONMENT', 'unknown')
        debug = 'DEBUG' if settings.DEBUG else 'PRODUCTION'
        
        self.stdout.write('=' * 70)
        self.stdout.write(
            self.style.SUCCESS(
                f'WhatsApp Integration Diagnostic - {timestamp}'
            )
        )
        self.stdout.write(f'Environment: {environment} ({debug})')
        self.stdout.write('=' * 70)
        self.stdout.write('')

    def check_environment_variables(self, verbose):
        """Verifica variáveis de ambiente"""
        self.stdout.write(self.style.WARNING('[ENV] Variáveis de Ambiente'))
        self.stdout.write('-' * 70)
        
        env_vars = {
            'WHATSAPP_PROVIDER': os.environ.get('WHATSAPP_PROVIDER', 'Não definido'),
            'WHATSAPP_GATEWAY_PROVIDER': os.environ.get('WHATSAPP_GATEWAY_PROVIDER', 'Não definido'),
            'WHATSAPP_SEND_ENABLED': os.environ.get('WHATSAPP_SEND_ENABLED', 'Não definido'),
            'WHATSAPP_SHADOW_MODE': os.environ.get('WHATSAPP_SHADOW_MODE', 'Não definido'),
            'WHATSAPP_CANONICAL_EVENTS_ENABLED': os.environ.get('WHATSAPP_CANONICAL_EVENTS_ENABLED', 'Não definido'),
            'WHATSAPP_CANONICAL_SHADOW_MODE': os.environ.get('WHATSAPP_CANONICAL_SHADOW_MODE', 'Não definido'),
            'WHATSAPP_ROUTING_ENABLED': os.environ.get('WHATSAPP_ROUTING_ENABLED', 'Não definido'),
            'WHATSAPP_SIM_ENABLED': os.environ.get('WHATSAPP_SIM_ENABLED', 'Não definido'),
        }
        
        all_ok = True
        for var_name, var_value in env_vars.items():
            if var_value == 'Não definido':
                self.stdout.write(f'  ⚠ {var_name}: {var_value}')
                self.status_warn.append(f'Variável {var_name} não definida')
                all_ok = False
            else:
                # Não exibir valores sensíveis
                if 'TOKEN' in var_name or 'KEY' in var_name or 'SECRET' in var_name:
                    display_value = '*** (oculto)'
                else:
                    display_value = var_value
                self.stdout.write(f'  ✓ {var_name}: {display_value}')
        
        if all_ok:
            self.status_ok.append('Todas as variáveis de ambiente definidas')
        else:
            self.recommendations.append(
                'Defina variáveis de ambiente faltantes para habilitar funcionalidades'
            )
        
        self.stdout.write('')

    def check_provider(self, verbose):
        """Verifica provider ativo"""
        self.stdout.write(self.style.WARNING('[PROVIDER] Provider Ativo'))
        self.stdout.write('-' * 70)
        
        if not WHATSAPP_GATEWAY_AVAILABLE:
            self.stdout.write('  ✗ WhatsApp Gateway não disponível (módulo não encontrado)')
            self.status_fail.append('WhatsApp Gateway não disponível')
            self.stdout.write('')
            return
        
        try:
            provider_name = get_whatsapp_provider()
            self.stdout.write(f'  ✓ Provider selecionado: {provider_name}')
            self.status_ok.append(f'Provider {provider_name} selecionado')
            
            # Verificar se send está habilitado
            send_enabled = is_whatsapp_send_enabled()
            if send_enabled:
                self.stdout.write('  ⚠ WHATSAPP_SEND_ENABLED: True (mensagens serão enviadas)')
                self.status_warn.append('Envio de mensagens habilitado')
                self.recommendations.append(
                    'Para testar em dev, defina WHATSAPP_SEND_ENABLED=False'
                )
            else:
                self.stdout.write('  ✓ WHATSAPP_SEND_ENABLED: False (modo seguro)')
                self.status_ok.append('Envio de mensagens desabilitado (modo seguro)')
            
            # Verificar shadow mode
            shadow_mode = is_whatsapp_shadow_mode()
            if shadow_mode:
                self.stdout.write('  ✓ WHATSAPP_SHADOW_MODE: True (modo shadow ativo)')
                self.status_ok.append('Shadow mode ativo')
            else:
                self.stdout.write('  ⚠ WHATSAPP_SHADOW_MODE: False')
                self.status_warn.append('Shadow mode desabilitado')
                self.recommendations.append(
                    'Para testar sem enviar mensagens, defina WHATSAPP_SHADOW_MODE=True'
                )
            
            # Verificar shoppers habilitados
            enabled_shoppers = get_enabled_shoppers()
            if enabled_shoppers:
                self.stdout.write(f'  ✓ Shoppers habilitados: {len(enabled_shoppers)}')
                if verbose:
                    for shopper in enabled_shoppers[:5]:  # Mostrar apenas 5
                        self.stdout.write(f'    - {shopper}')
                    if len(enabled_shoppers) > 5:
                        self.stdout.write(f'    ... e mais {len(enabled_shoppers) - 5}')
            else:
                self.stdout.write('  ⚠ Nenhum shopper habilitado (WHATSAPP_ENABLED_SHOPPERS vazio)')
                self.status_warn.append('Nenhum shopper habilitado')
            
            # Healthcheck do provider
            try:
                gateway = get_whatsapp_gateway()
                health = gateway.healthcheck()
                if health.is_healthy():
                    self.stdout.write(f'  ✓ Provider saudável: {health.message}')
                    self.status_ok.append('Provider responde ao healthcheck')
                else:
                    self.stdout.write(f'  ✗ Provider não saudável ({health.status}): {health.message}')
                    self.status_fail.append(f'Provider não saudável ({health.status}): {health.message}')
            except Exception as e:
                self.stdout.write(f'  ✗ Erro ao verificar healthcheck: {str(e)}')
                self.status_fail.append(f'Erro no healthcheck: {str(e)}')
        
        except Exception as e:
            self.stdout.write(f'  ✗ Erro ao verificar provider: {str(e)}')
            self.status_fail.append(f'Erro ao verificar provider: {str(e)}')
        
        self.stdout.write('')

    def check_shadow_mode(self, verbose):
        """Verifica shadow mode e publisher canônico"""
        self.stdout.write(self.style.WARNING('[SHADOW MODE] Modo Shadow e Publisher Canônico'))
        self.stdout.write('-' * 70)
        
        # Verificar shadow mode de eventos canônicos
        canonical_shadow = getattr(settings, 'WHATSAPP_CANONICAL_SHADOW_MODE', False)
        if canonical_shadow:
            self.stdout.write('  ✓ WHATSAPP_CANONICAL_SHADOW_MODE: True')
            self.status_ok.append('Shadow mode de eventos canônicos ativo')
        else:
            self.stdout.write('  ⚠ WHATSAPP_CANONICAL_SHADOW_MODE: False')
            self.status_warn.append('Shadow mode de eventos canônicos desabilitado')
        
        # Verificar se eventos canônicos estão habilitados
        canonical_enabled = getattr(settings, 'WHATSAPP_CANONICAL_EVENTS_ENABLED', False)
        if canonical_enabled:
            self.stdout.write('  ✓ WHATSAPP_CANONICAL_EVENTS_ENABLED: True')
            self.status_ok.append('Eventos canônicos habilitados')
            
            # Verificar publisher
            if CANONICAL_PUBLISHER_AVAILABLE:
                try:
                    publisher = get_event_publisher()
                    self.stdout.write('  ✓ Publisher canônico inicializável')
                    self.status_ok.append('Publisher canônico disponível')
                except Exception as e:
                    self.stdout.write(f'  ✗ Erro ao inicializar publisher: {str(e)}')
                    self.status_fail.append(f'Erro ao inicializar publisher: {str(e)}')
            else:
                self.stdout.write('  ✗ Publisher canônico não disponível (módulo não encontrado)')
                self.status_fail.append('Publisher canônico não disponível')
        else:
            self.stdout.write('  ⚠ WHATSAPP_CANONICAL_EVENTS_ENABLED: False')
            self.status_warn.append('Eventos canônicos desabilitados')
            self.recommendations.append(
                'Para habilitar eventos canônicos, defina WHATSAPP_CANONICAL_EVENTS_ENABLED=True'
            )
        
        self.stdout.write('')

    def check_webhook_endpoints(self, verbose):
        """Verifica endpoints de webhook registrados"""
        self.stdout.write(self.style.WARNING('[WEBHOOK] Endpoints de Webhook'))
        self.stdout.write('-' * 70)
        
        try:
            resolver = get_resolver()
            webhook_patterns = []
            
            def find_webhook_urls(urlpatterns, prefix=''):
                for pattern in urlpatterns:
                    if hasattr(pattern, 'url_patterns'):
                        find_webhook_urls(pattern.url_patterns, prefix + str(pattern.pattern))
                    elif hasattr(pattern, 'pattern'):
                        url = prefix + str(pattern.pattern)
                        # Buscar padrões relacionados a webhook/whatsapp
                        if 'webhook' in url.lower() or 'whatsapp' in url.lower():
                            webhook_patterns.append(url)
            
            find_webhook_urls(resolver.url_patterns)
            
            if webhook_patterns:
                self.stdout.write(f'  ✓ {len(webhook_patterns)} endpoint(s) de webhook encontrado(s):')
                for pattern in webhook_patterns[:10]:  # Mostrar apenas 10
                    self.stdout.write(f'    - {pattern}')
                if len(webhook_patterns) > 10:
                    self.stdout.write(f'    ... e mais {len(webhook_patterns) - 10}')
                self.status_ok.append(f'{len(webhook_patterns)} endpoint(s) de webhook registrado(s)')
            else:
                self.stdout.write('  ⚠ Nenhum endpoint de webhook encontrado')
                self.status_warn.append('Nenhum endpoint de webhook encontrado')
                self.recommendations.append(
                    'Verifique se os endpoints de webhook estão registrados em urls.py'
                )
        except Exception as e:
            self.stdout.write(f'  ✗ Erro ao verificar endpoints: {str(e)}')
            self.status_fail.append(f'Erro ao verificar endpoints: {str(e)}')
        
        self.stdout.write('')
        self.stdout.write('  ℹ Nota: Apenas validação local. Não faz chamadas externas.')

    def check_database(self, verbose):
        """Verifica tabelas de banco de dados"""
        self.stdout.write(self.style.WARNING('[DATABASE] Tabelas de Banco de Dados'))
        self.stdout.write('-' * 70)
        
        tables_to_check = []
        
        # WhatsAppEventLog
        if WHATSAPP_EVENTS_AVAILABLE:
            tables_to_check.append(('app_whatsapp_events_eventlog', 'WhatsAppEventLog'))
            tables_to_check.append(('app_whatsapp_events_conversation', 'WhatsAppConversation'))
        
        # CanonicalEventLog
        if CANONICAL_EVENTS_AVAILABLE:
            tables_to_check.append(('core_whatsapp_canonical_event_log', 'CanonicalEventLog'))
        
        # SimulatedMessage
        if SIMULATED_MESSAGES_AVAILABLE:
            tables_to_check.append(('core_whatsapp_simulated_message', 'SimulatedMessage'))
        
        with connection.cursor() as cursor:
            for table_name, model_name in tables_to_check:
                try:
                    # PostgreSQL usa lower case para nomes de tabelas em information_schema
                    cursor.execute(
                        "SELECT EXISTS (SELECT FROM information_schema.tables WHERE LOWER(table_name) = LOWER(%s))",
                        [table_name]
                    )
                    exists = cursor.fetchone()[0]
                    
                    if exists:
                        # Contar eventos recentes (últimas 24h)
                        try:
                            if 'eventlog' in table_name.lower() or 'canonical' in table_name.lower():
                                # Tabela de eventos - usar timestamp ou created_at
                                try:
                                    cursor.execute(
                                        f'SELECT COUNT(*) FROM "{table_name}" WHERE created_at >= %s',
                                        [datetime.now() - timedelta(hours=24)]
                                    )
                                except:
                                    # Tentar com timestamp se created_at não existir
                                    cursor.execute(
                                        f'SELECT COUNT(*) FROM "{table_name}" WHERE timestamp >= %s',
                                        [datetime.now() - timedelta(hours=24)]
                                    )
                                count = cursor.fetchone()[0]
                                self.stdout.write(f'  ✓ {model_name}: Existe ({count} eventos nas últimas 24h)')
                                self.status_ok.append(f'Tabela {model_name} existe')
                            elif 'conversation' in table_name.lower():
                                # Tabela de conversas
                                cursor.execute(f'SELECT COUNT(*) FROM "{table_name}"')
                                count = cursor.fetchone()[0]
                                self.stdout.write(f'  ✓ {model_name}: Existe ({count} conversa(s))')
                                self.status_ok.append(f'Tabela {model_name} existe')
                            elif 'simulated' in table_name.lower():
                                # Tabela de mensagens simuladas
                                cursor.execute(f'SELECT COUNT(*) FROM "{table_name}"')
                                count = cursor.fetchone()[0]
                                self.stdout.write(f'  ✓ {model_name}: Existe ({count} mensagem(ns) simulada(s))')
                                self.status_ok.append(f'Tabela {model_name} existe')
                            else:
                                self.stdout.write(f'  ✓ {model_name}: Existe')
                                self.status_ok.append(f'Tabela {model_name} existe')
                        except Exception as e:
                            self.stdout.write(f'  ⚠ {model_name}: Existe (erro ao contar: {str(e)})')
                            self.status_warn.append(f'Erro ao contar registros em {model_name}')
                    else:
                        self.stdout.write(f'  ✗ {model_name}: Não existe')
                        self.status_fail.append(f'Tabela {model_name} não existe')
                        self.recommendations.append(
                            f'Execute migrations para criar tabela {model_name}'
                        )
                except Exception as e:
                    self.stdout.write(f'  ✗ {model_name}: Erro ao verificar ({str(e)})')
                    self.status_fail.append(f'Erro ao verificar {model_name}: {str(e)}')
        
        self.stdout.write('')

    def check_simulator(self, verbose):
        """Verifica simulador (se habilitado)"""
        self.stdout.write(self.style.WARNING('[SIMULATOR] Simulador de Mensagens'))
        self.stdout.write('-' * 70)
        
        sim_enabled = os.environ.get('WHATSAPP_SIM_ENABLED', 'False').lower() in ('true', '1', 'yes')
        
        if sim_enabled:
            self.stdout.write('  ✓ WHATSAPP_SIM_ENABLED: True')
            self.status_ok.append('Simulador habilitado')
            
            if SIMULATED_MESSAGES_AVAILABLE:
                try:
                    count = SimulatedMessage.objects.count()
                    self.stdout.write(f'  ✓ {count} mensagem(ns) simulada(s) no banco')
                    self.status_ok.append(f'{count} mensagem(ns) simulada(s)')
                except Exception as e:
                    self.stdout.write(f'  ✗ Erro ao contar mensagens simuladas: {str(e)}')
                    self.status_fail.append(f'Erro ao contar mensagens simuladas: {str(e)}')
            else:
                self.stdout.write('  ✗ Model SimulatedMessage não disponível')
                self.status_fail.append('Model SimulatedMessage não disponível')
        else:
            self.stdout.write('  ⚠ WHATSAPP_SIM_ENABLED: False (simulador desabilitado)')
            self.status_warn.append('Simulador desabilitado')
            self.recommendations.append(
                'Para testar com simulador, defina WHATSAPP_SIM_ENABLED=True'
            )
        
        self.stdout.write('')

    def print_summary(self):
        """Imprime resumo final"""
        self.stdout.write('=' * 70)
        self.stdout.write(self.style.WARNING('RESUMO'))
        self.stdout.write('=' * 70)
        
        self.stdout.write(f'\n✓ OK: {len(self.status_ok)}')
        self.stdout.write(f'⚠ WARN: {len(self.status_warn)}')
        self.stdout.write(f'✗ FAIL: {len(self.status_fail)}')
        
        if self.status_fail:
            self.stdout.write('\n' + self.style.ERROR('Falhas:'))
            for fail in self.status_fail:
                self.stdout.write(f'  ✗ {fail}')
        
        if self.status_warn:
            self.stdout.write('\n' + self.style.WARNING('Avisos:'))
            for warn in self.status_warn:
                self.stdout.write(f'  ⚠ {warn}')
        
        if self.recommendations:
            self.stdout.write('\n' + self.style.SUCCESS('Recomendações:'))
            for rec in self.recommendations:
                self.stdout.write(f'  → {rec}')
        
        self.stdout.write('')
