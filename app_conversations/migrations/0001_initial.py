# ============================================================================
# ARQUITETURA NOVA - app_conversations
# ============================================================================
# Generated migration for Conversation, Message, Suggestion
# ============================================================================

from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('app_whatsapp_gateway', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Conversation',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('shopper_id', models.CharField(db_index=True, help_text='ID do Shopper (UUID do VitrineZap) - Multi-tenant', max_length=100)),
                ('instance_id', models.CharField(db_index=True, help_text='ID da instância Evolution (FK para app_whatsapp_gateway.EvolutionInstance)', max_length=100)),
                ('conversation_key', models.CharField(db_index=True, help_text="Chave única da conversa (ex: 'whatsapp:+5511999999999' ou 'whatsapp_group:123')", max_length=200)),
                ('customer_phone', models.CharField(db_index=True, help_text='Telefone do cliente (formato: +5511999999999)', max_length=20)),
                ('customer_name', models.CharField(blank=True, help_text='Nome do cliente (opcional)', max_length=200, null=True)),
                ('chat_type', models.CharField(choices=[('private', 'Privada'), ('group', 'Grupo')], default='private', max_length=10)),
                ('owner', models.CharField(choices=[('AI', 'IA'), ('SHOPPER', 'Shopper')], default='AI', max_length=10)),
                ('mode', models.CharField(choices=[('assistido', 'Assistido'), ('auto', 'Automático')], default='assistido', max_length=10)),
                ('tags', models.JSONField(blank=True, default=list, help_text="Tags da conversa (ex: ['venda', 'suporte'])")),
                ('last_message_at', models.DateTimeField(blank=True, db_index=True, help_text='Timestamp da última mensagem', null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'verbose_name': 'Conversa (Nova Arquitetura)',
                'verbose_name_plural': 'Conversas (Nova Arquitetura)',
                'ordering': ['-last_message_at', '-created_at'],
            },
        ),
        migrations.CreateModel(
            name='Message',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('direction', models.CharField(choices=[('in', 'Entrada'), ('out', 'Saída')], max_length=3)),
                ('message_type', models.CharField(choices=[('text', 'Texto'), ('image', 'Imagem'), ('audio', 'Áudio'), ('video', 'Vídeo'), ('file', 'Arquivo'), ('interactive', 'Interativo'), ('unknown', 'Desconhecido')], default='text', max_length=20)),
                ('text', models.TextField(blank=True, help_text='Texto da mensagem', null=True)),
                ('media_url', models.URLField(blank=True, help_text='URL da mídia (se houver)', null=True)),
                ('provider', models.CharField(default='evolution', help_text="Provedor (ex: 'evolution')", max_length=50)),
                ('raw_payload', models.JSONField(blank=True, default=dict, help_text='Payload original do provedor')),
                ('sent_by', models.CharField(choices=[('customer', 'Cliente'), ('ai', 'IA'), ('shopper', 'Shopper'), ('system', 'Sistema')], default='customer', max_length=10)),
                ('timestamp', models.DateTimeField(db_index=True, help_text='Timestamp da mensagem (do WhatsApp)')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('conversation', models.ForeignKey(help_text='Conversa à qual a mensagem pertence', on_delete=django.db.models.deletion.CASCADE, related_name='messages', to='app_conversations.conversation')),
            ],
            options={
                'verbose_name': 'Mensagem (Nova Arquitetura)',
                'verbose_name_plural': 'Mensagens (Nova Arquitetura)',
                'ordering': ['timestamp', 'created_at'],
            },
        ),
        migrations.CreateModel(
            name='Suggestion',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('intent', models.CharField(blank=True, help_text="Intenção detectada pela IA (ex: 'buscar_produto', 'fazer_pedido')", max_length=100, null=True)),
                ('confidence', models.FloatField(default=0.0, help_text='Confiança da IA (0.0 a 1.0)')),
                ('suggested_reply', models.TextField(help_text='Resposta sugerida pela IA')),
                ('actions', models.JSONField(blank=True, default=list, help_text="Ações sugeridas (ex: [{'tool': 'catalog.search', 'args': {...}}])")),
                ('status', models.CharField(choices=[('pending', 'Pendente'), ('sent', 'Enviada'), ('dismissed', 'Descartada')], db_index=True, default='pending', max_length=10)),
                ('created_at', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('sent_at', models.DateTimeField(blank=True, help_text='Quando a sugestão foi enviada (se status=sent)', null=True)),
                ('conversation', models.ForeignKey(help_text='Conversa à qual a sugestão pertence', on_delete=django.db.models.deletion.CASCADE, related_name='suggestions', to='app_conversations.conversation')),
            ],
            options={
                'verbose_name': 'Sugestão de IA',
                'verbose_name_plural': 'Sugestões de IA',
                'ordering': ['-created_at'],
            },
        ),
        migrations.AddIndex(
            model_name='conversation',
            index=models.Index(fields=['shopper_id', '-last_message_at'], name='app_convers_shopper_5a8f3d_idx'),
        ),
        migrations.AddIndex(
            model_name='conversation',
            index=models.Index(fields=['conversation_key'], name='app_convers_convers_9c7d4e_idx'),
        ),
        migrations.AddIndex(
            model_name='conversation',
            index=models.Index(fields=['customer_phone', '-last_message_at'], name='app_convers_custome_2f8a9b_idx'),
        ),
        migrations.AddIndex(
            model_name='conversation',
            index=models.Index(fields=['owner', 'mode'], name='app_convers_owner__3e9f7a_idx'),
        ),
        migrations.AlterUniqueTogether(
            name='conversation',
            unique_together={('shopper_id', 'conversation_key')},
        ),
        migrations.AddIndex(
            model_name='message',
            index=models.Index(fields=['conversation', 'timestamp'], name='app_convers_convers_4f8a9b_idx'),
        ),
        migrations.AddIndex(
            model_name='message',
            index=models.Index(fields=['direction', 'timestamp'], name='app_convers_direct_5a8f3d_idx'),
        ),
        migrations.AddIndex(
            model_name='message',
            index=models.Index(fields=['sent_by', 'timestamp'], name='app_convers_sent_by_6c9e4f_idx'),
        ),
        migrations.AddIndex(
            model_name='suggestion',
            index=models.Index(fields=['conversation', '-created_at'], name='app_convers_convers_7d9f5e_idx'),
        ),
        migrations.AddIndex(
            model_name='suggestion',
            index=models.Index(fields=['status', '-created_at'], name='app_convers_status__8e0f6a_idx'),
        ),
        migrations.AddIndex(
            model_name='suggestion',
            index=models.Index(fields=['intent', '-created_at'], name='app_convers_intent__9f1g7b_idx'),
        ),
    ]

