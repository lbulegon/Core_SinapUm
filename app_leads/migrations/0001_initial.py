# Generated manually for Lead Registry

import django.utils.timezone
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='ProjectCredential',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('project_key', models.CharField(help_text='Identificador único do projeto (ex: vitrinezap, motopro, eventix)', max_length=50, unique=True)),
                ('project_secret', models.CharField(help_text='Secret para geração de assinatura HMAC (armazenar de forma segura)', max_length=255)),
                ('is_active', models.BooleanField(default=True, help_text='Se False, o projeto não pode mais publicar leads')),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'verbose_name': 'Credencial de Projeto',
                'verbose_name_plural': 'Credenciais de Projetos',
                'ordering': ['-created_at'],
            },
        ),
        migrations.CreateModel(
            name='Lead',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nome', models.CharField(max_length=120)),
                ('email', models.EmailField(max_length=254)),
                ('whatsapp', models.CharField(max_length=32)),
                ('cidade', models.CharField(blank=True, max_length=120)),
                ('source_system', models.CharField(default='unknown', help_text='Sistema que gerou o lead (vitrinezap, motopro, eventix, etc.)', max_length=50)),
                ('source_entrypoint', models.CharField(blank=True, help_text='Ponto de entrada (home, modal, landing, etc.)', max_length=80)),
                ('source_context', models.CharField(blank=True, help_text='Contexto específico (lista_antecipada, cadastro, download, etc.)', max_length=80)),
                ('utm_source', models.CharField(blank=True, max_length=120)),
                ('utm_campaign', models.CharField(blank=True, max_length=120)),
                ('utm_medium', models.CharField(blank=True, max_length=120)),
                ('utm_content', models.CharField(blank=True, max_length=120)),
                ('lead_status', models.CharField(choices=[('new', 'Novo'), ('qualified', 'Qualificado'), ('activated', 'Ativado'), ('dormant', 'Inativo')], default='new', max_length=30)),
                ('is_opt_out', models.BooleanField(default=False, help_text='Se True, o lead optou por não receber comunicações')),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'verbose_name': 'Lead',
                'verbose_name_plural': 'Leads',
                'ordering': ['-created_at'],
            },
        ),
        migrations.CreateModel(
            name='LeadEvent',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('event_type', models.CharField(choices=[('created', 'Criado'), ('updated', 'Atualizado'), ('rejected', 'Rejeitado'), ('rate_limited', 'Rate Limited'), ('opt_out', 'Opt-out')], max_length=40)),
                ('ip', models.GenericIPAddressField(blank=True, null=True)),
                ('user_agent', models.TextField(blank=True)),
                ('referrer', models.TextField(blank=True)),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now)),
                ('lead', models.ForeignKey(blank=True, help_text='Pode ser None para eventos de rejeição/rate_limit antes da criação do lead', null=True, on_delete=django.db.models.deletion.CASCADE, related_name='events', to='app_leads.lead')),
            ],
            options={
                'verbose_name': 'Evento de Lead',
                'verbose_name_plural': 'Eventos de Leads',
                'ordering': ['-created_at'],
            },
        ),
        migrations.AddIndex(
            model_name='projectcredential',
            index=models.Index(fields=['project_key'], name='app_leads_p_project__idx'),
        ),
        migrations.AddIndex(
            model_name='projectcredential',
            index=models.Index(fields=['is_active'], name='app_leads_p_is_acti_idx'),
        ),
        migrations.AddIndex(
            model_name='lead',
            index=models.Index(fields=['email'], name='app_leads_l_email_idx'),
        ),
        migrations.AddIndex(
            model_name='lead',
            index=models.Index(fields=['whatsapp'], name='app_leads_l_whatsap_idx'),
        ),
        migrations.AddIndex(
            model_name='lead',
            index=models.Index(fields=['source_system'], name='app_leads_l_source__idx'),
        ),
        migrations.AddIndex(
            model_name='lead',
            index=models.Index(fields=['created_at'], name='app_leads_lead_created_idx'),
        ),
        migrations.AddIndex(
            model_name='lead',
            index=models.Index(fields=['lead_status'], name='app_leads_lead_status_idx'),
        ),
        migrations.AddIndex(
            model_name='leadevent',
            index=models.Index(fields=['lead', 'created_at'], name='app_leads_event_lead_idx'),
        ),
        migrations.AddIndex(
            model_name='leadevent',
            index=models.Index(fields=['event_type'], name='app_leads_event_type_idx'),
        ),
        migrations.AddIndex(
            model_name='leadevent',
            index=models.Index(fields=['created_at'], name='app_leads_event_created_idx'),
        ),
    ]

