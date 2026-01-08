# Generated migration - WhatsApp Events

from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='WhatsAppConversation',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('conversation_id', models.CharField(db_index=True, help_text='ID único da conversação', max_length=255, unique=True)),
                ('thread_key', models.CharField(db_index=True, help_text='Chave do thread (determinística)', max_length=500, unique=True)),
                ('shopper_id', models.CharField(blank=True, db_index=True, help_text='ID do shopper', max_length=255, null=True)),
                ('skm_id', models.CharField(blank=True, db_index=True, help_text='ID do SKM atribuído', max_length=255, null=True)),
                ('keeper_id', models.CharField(blank=True, db_index=True, help_text='ID do keeper', max_length=255, null=True)),
                ('status', models.CharField(choices=[('open', 'Aberta'), ('closed', 'Fechada'), ('archived', 'Arquivada')], db_index=True, default='open', help_text='Status da conversação', max_length=20)),
                ('last_event_at', models.DateTimeField(blank=True, db_index=True, help_text='Timestamp do último evento', null=True)),
                ('last_actor_wa_id', models.CharField(blank=True, help_text='WhatsApp ID do último ator', max_length=50, null=True)),
                ('tags', models.JSONField(blank=True, default=list, help_text='Tags da conversação')),
                ('created_at', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('closed_at', models.DateTimeField(blank=True, help_text='Timestamp de fechamento', null=True)),
            ],
            options={
                'verbose_name': 'WhatsApp Conversation',
                'verbose_name_plural': 'WhatsApp Conversations',
                'db_table': 'app_whatsapp_events_conversation',
                'ordering': ['-last_event_at', '-created_at'],
            },
        ),
        migrations.CreateModel(
            name='WhatsAppEventLog',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('event_id', models.CharField(db_index=True, help_text='ID único do evento', max_length=255, unique=True)),
                ('event_type', models.CharField(db_index=True, help_text='Tipo do evento canônico', max_length=100)),
                ('event_version', models.CharField(default='1.0', help_text='Versão do schema', max_length=10)),
                ('occurred_at', models.DateTimeField(db_index=True, help_text='Timestamp do evento')),
                ('provider', models.CharField(db_index=True, help_text='Provider: evolution, cloud, baileys, etc.', max_length=50)),
                ('provider_account_id', models.CharField(blank=True, help_text='ID da conta no provider', max_length=255, null=True)),
                ('provider_message_id', models.CharField(blank=True, db_index=True, help_text='ID da mensagem no provider', max_length=255, null=True)),
                ('webhook_id', models.CharField(blank=True, help_text='ID do webhook', max_length=255, null=True)),
                ('idempotency_key', models.CharField(db_index=True, help_text='Chave de idempotência (determinística)', max_length=255, unique=True)),
                ('correlation_id', models.CharField(blank=True, db_index=True, help_text='ID de correlação', max_length=255, null=True)),
                ('parent_event_id', models.CharField(blank=True, db_index=True, help_text='ID do evento pai', max_length=255, null=True)),
                ('shopper_id', models.CharField(blank=True, db_index=True, help_text='ID do shopper', max_length=255, null=True)),
                ('skm_id', models.CharField(blank=True, db_index=True, help_text='ID do SKM (Sales Keeper Mesh)', max_length=255, null=True)),
                ('keeper_id', models.CharField(blank=True, db_index=True, help_text='ID do keeper', max_length=255, null=True)),
                ('conversation_id', models.CharField(blank=True, db_index=True, help_text='ID da conversação', max_length=255, null=True)),
                ('thread_key', models.CharField(blank=True, db_index=True, help_text='Chave do thread (determinística)', max_length=500, null=True)),
                ('actor_wa_id', models.CharField(blank=True, db_index=True, help_text='WhatsApp ID do ator', max_length=50, null=True)),
                ('actor_role', models.CharField(blank=True, help_text='Role: customer, skm, shopper, keeper, system', max_length=50, null=True)),
                ('chat_type', models.CharField(blank=True, help_text='Tipo: private, group', max_length=20, null=True)),
                ('group_id', models.CharField(blank=True, db_index=True, help_text='ID do grupo (se aplicável)', max_length=255, null=True)),
                ('message_type', models.CharField(blank=True, help_text='Tipo: text, media, interactive, etc.', max_length=50, null=True)),
                ('message_direction', models.CharField(blank=True, help_text='Direção: inbound, outbound', max_length=20, null=True)),
                ('payload_json', models.JSONField(blank=True, default=dict, help_text='Payload específico do evento (JSON)')),
                ('raw_provider_payload', models.JSONField(blank=True, default=dict, help_text='Payload bruto do provider (JSON)')),
                ('signature_valid', models.BooleanField(default=True, help_text='Se assinatura é válida')),
                ('risk_flags', models.JSONField(blank=True, default=list, help_text='Flags de risco')),
                ('created_at', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('processed_at', models.DateTimeField(blank=True, help_text='Timestamp de processamento', null=True)),
            ],
            options={
                'verbose_name': 'WhatsApp Event Log',
                'verbose_name_plural': 'WhatsApp Event Logs',
                'db_table': 'app_whatsapp_events_eventlog',
                'ordering': ['-occurred_at', '-created_at'],
            },
        ),
        migrations.CreateModel(
            name='WhatsAppThreadParticipant',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('wa_id', models.CharField(db_index=True, help_text='WhatsApp ID do participante', max_length=50)),
                ('role', models.CharField(choices=[('customer', 'Cliente'), ('skm', 'SKM'), ('shopper', 'Shopper'), ('keeper', 'Keeper'), ('system', 'Sistema')], db_index=True, help_text='Role do participante', max_length=20)),
                ('display_name', models.CharField(blank=True, help_text='Nome de exibição', max_length=255, null=True)),
                ('first_seen_at', models.DateTimeField(auto_now_add=True, help_text='Primeira vez visto')),
                ('last_seen_at', models.DateTimeField(auto_now=True, db_index=True, help_text='Última vez visto')),
                ('is_blocked', models.BooleanField(default=False, help_text='Se está bloqueado')),
                ('conversation', models.ForeignKey(help_text='Conversação', on_delete=django.db.models.deletion.CASCADE, related_name='participants', to='app_whatsapp_events.whatsappconversation')),
            ],
            options={
                'verbose_name': 'WhatsApp Thread Participant',
                'verbose_name_plural': 'WhatsApp Thread Participants',
                'db_table': 'app_whatsapp_events_threadparticipant',
                'ordering': ['-last_seen_at'],
                'unique_together': {('conversation', 'wa_id')},
            },
        ),
        migrations.CreateModel(
            name='WhatsAppMessageIndex',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('provider_message_id', models.CharField(db_index=True, help_text='ID da mensagem no provider', max_length=255, unique=True)),
                ('message_id', models.UUIDField(db_index=True, help_text='ID interno da mensagem (event_id)')),
                ('direction', models.CharField(db_index=True, help_text='Direção: inbound, outbound', max_length=20)),
                ('message_type', models.CharField(db_index=True, help_text='Tipo: text, media, etc.', max_length=50)),
                ('occurred_at', models.DateTimeField(db_index=True, help_text='Timestamp do evento')),
                ('conversation', models.ForeignKey(help_text='Conversação', on_delete=django.db.models.deletion.CASCADE, related_name='message_indexes', to='app_whatsapp_events.whatsappconversation')),
            ],
            options={
                'verbose_name': 'WhatsApp Message Index',
                'verbose_name_plural': 'WhatsApp Message Indexes',
                'db_table': 'app_whatsapp_events_messageindex',
                'ordering': ['-occurred_at'],
            },
        ),
        migrations.AddIndex(
            model_name='whatsappeventlog',
            index=models.Index(fields=['thread_key', '-occurred_at'], name='app_whatsap_thread__idx'),
        ),
        migrations.AddIndex(
            model_name='whatsappeventlog',
            index=models.Index(fields=['provider_message_id'], name='app_whatsap_provider_idx'),
        ),
        migrations.AddIndex(
            model_name='whatsappeventlog',
            index=models.Index(fields=['occurred_at'], name='app_whatsap_occurre_idx'),
        ),
        migrations.AddIndex(
            model_name='whatsappeventlog',
            index=models.Index(fields=['event_type', '-occurred_at'], name='app_whatsap_event_t_idx'),
        ),
        migrations.AddIndex(
            model_name='whatsappeventlog',
            index=models.Index(fields=['provider', '-occurred_at'], name='app_whatsap_provide_idx'),
        ),
        migrations.AddIndex(
            model_name='whatsappeventlog',
            index=models.Index(fields=['conversation_id', '-occurred_at'], name='app_whatsap_events_conv_idx'),
        ),
        migrations.AddIndex(
            model_name='whatsappeventlog',
            index=models.Index(fields=['shopper_id', '-occurred_at'], name='app_whatsap_events_shopper_idx'),
        ),
        migrations.AddIndex(
            model_name='whatsappeventlog',
            index=models.Index(fields=['skm_id', '-occurred_at'], name='app_whatsap_events_skm_idx'),
        ),
        migrations.AddIndex(
            model_name='whatsappconversation',
            index=models.Index(fields=['last_event_at'], name='app_whatsap_last_eve_idx'),
        ),
        migrations.AddIndex(
            model_name='whatsappconversation',
            index=models.Index(fields=['status', '-last_event_at'], name='app_whatsap_status__idx'),
        ),
        migrations.AddIndex(
            model_name='whatsappconversation',
            index=models.Index(fields=['shopper_id', '-last_event_at'], name='app_whatsap_conv_shopper_idx'),
        ),
        migrations.AddIndex(
            model_name='whatsappconversation',
            index=models.Index(fields=['skm_id', '-last_event_at'], name='app_whatsap_conv_skm_idx'),
        ),
        migrations.AddIndex(
            model_name='whatsappthreadparticipant',
            index=models.Index(fields=['role', '-last_seen_at'], name='app_whatsap_role_las_idx'),
        ),
        migrations.AddIndex(
            model_name='whatsappmessageindex',
            index=models.Index(fields=['conversation', '-occurred_at'], name='app_whatsap_msg_conv_idx'),
        ),
        migrations.AddIndex(
            model_name='whatsappmessageindex',
            index=models.Index(fields=['direction', '-occurred_at'], name='app_whatsap_msg_dir_idx'),
        ),
    ]
