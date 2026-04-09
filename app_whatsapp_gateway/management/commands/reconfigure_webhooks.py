"""
Management command para reconfigurar webhooks de instâncias existentes
======================================================================

Instâncias criadas antes da implementação de webhook por instância
não têm a URL configurada. Este comando aplica o webhook correto
em todas as instâncias Evolution.

Uso:
    python manage.py reconfigure_webhooks
    python manage.py reconfigure_webhooks --instance shopper_123
    python manage.py reconfigure_webhooks --dry-run
"""
from django.core.management.base import BaseCommand
from django.conf import settings

from app_whatsapp_gateway.models import EvolutionInstance
from app_whatsapp_gateway.clients import EvolutionClient
from app_whatsapp_gateway.services import InstanceService


class Command(BaseCommand):
    help = 'Reconfigura webhook por instância para instâncias Evolution existentes'

    def add_arguments(self, parser):
        parser.add_argument(
            '--instance',
            type=str,
            help='Reconfigurar apenas esta instância (instance_id)',
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Apenas listar o que seria feito, sem alterar',
        )
        parser.add_argument(
            '--create-missing',
            action='store_true',
            help='Criar instância na Evolution API se não existir (e depois configurar webhook)',
        )

    def handle(self, *args, **options):
        instance_filter = options.get('instance')
        dry_run = options.get('dry_run')
        create_missing = options.get('create_missing', False)

        webhook_base = getattr(settings, 'EVOLUTION_WEBHOOK_BASE_URL', '')
        if not webhook_base:
            self.stdout.write(
                self.style.ERROR(
                    'EVOLUTION_WEBHOOK_BASE_URL não configurada em settings. '
                    'Defina a variável de ambiente antes de executar.'
                )
            )
            return

        queryset = EvolutionInstance.objects.filter(is_active=True)
        if instance_filter:
            queryset = queryset.filter(instance_id=instance_filter)
            if not queryset.exists():
                self.stdout.write(
                    self.style.ERROR(f'Instância "{instance_filter}" não encontrada.')
                )
                return

        instances = list(queryset.order_by('shopper_id'))
        if not instances:
            self.stdout.write(self.style.WARNING('Nenhuma instância ativa encontrada.'))
            return

        if dry_run:
            self.stdout.write(self.style.WARNING('Modo dry-run - nenhuma alteração será feita\n'))
            for inst in instances:
                webhook_url = f"{webhook_base.rstrip('/')}/webhooks/evolution/{inst.instance_id}/messages"
                self.stdout.write(f"  {inst.instance_id} (shopper: {inst.shopper_id})")
                self.stdout.write(f"    → {webhook_url}\n")
            self.stdout.write(self.style.SUCCESS(f'Total: {len(instances)} instância(s)'))
            return

        client = EvolutionClient()
        ok = 0
        fail = 0

        instance_service = InstanceService() if create_missing else None

        for inst in instances:
            webhook_url = f"{webhook_base.rstrip('/')}/webhooks/evolution/{inst.instance_id}/messages"
            result = client.set_webhook(inst.instance_id, webhook_url)

            if result.get('error'):
                err = result.get('error', '')
                if create_missing and ('not found' in err.lower() or err == 'Not Found'):
                    self.stdout.write(f"  → {inst.instance_id}: criando na Evolution API...")
                    create_result = instance_service.create_instance(inst.shopper_id, inst.instance_id)
                    if create_result.get('success'):
                        self.stdout.write(
                            self.style.SUCCESS(f"✓ {inst.instance_id} (criada e webhook configurado)")
                        )
                        ok += 1
                    else:
                        self.stdout.write(
                            self.style.ERROR(f"✗ {inst.instance_id}: falha ao criar - {create_result.get('error')}")
                        )
                        fail += 1
                else:
                    hint = ''
                    if 'not found' in err.lower() or err == 'Not Found':
                        hint = ' (use --create-missing para criar a instância)'
                    self.stdout.write(
                        self.style.ERROR(f"✗ {inst.instance_id}: {err}{hint}")
                    )
                    fail += 1
            else:
                self.stdout.write(
                    self.style.SUCCESS(f"✓ {inst.instance_id} (shopper: {inst.shopper_id})")
                )
                ok += 1

        self.stdout.write('')
        self.stdout.write(self.style.SUCCESS(f'Concluído: {ok} ok, {fail} falha(s)'))
