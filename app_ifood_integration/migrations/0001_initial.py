# Generated migration for app_ifood_integration

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='IfoodStore',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nome', models.CharField(help_text='Nome da loja', max_length=120)),
                ('cnpj', models.CharField(blank=True, help_text='CNPJ da loja', max_length=18, null=True)),
                ('ifood_merchant_id', models.CharField(help_text='ID único da loja no iFood (merchantId ou storeId)', max_length=80, unique=True)),
                ('ativo', models.BooleanField(default=True, help_text='Loja ativa para sincronização')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'verbose_name': 'Loja iFood',
                'verbose_name_plural': 'Lojas iFood',
                'db_table': 'ifood_store',
                'ordering': ['nome'],
            },
        ),
        migrations.CreateModel(
            name='IfoodOAuthToken',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('access_token', models.TextField(help_text='Access token OAuth (criptografado em produção)')),
                ('refresh_token', models.TextField(help_text='Refresh token OAuth (criptografado em produção)')),
                ('token_type', models.CharField(default='Bearer', max_length=20)),
                ('expires_at', models.DateTimeField(help_text='Data/hora de expiração do access_token')),
                ('scope', models.TextField(blank=True, help_text='Escopos OAuth concedidos', null=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('store', models.OneToOneField(help_text='Loja associada ao token', on_delete=django.db.models.deletion.CASCADE, related_name='oauth_token', to='app_ifood_integration.ifoodstore')),
            ],
            options={
                'verbose_name': 'Token OAuth iFood',
                'verbose_name_plural': 'Tokens OAuth iFood',
                'db_table': 'ifood_oauth_token',
            },
        ),
        migrations.CreateModel(
            name='IfoodSyncRun',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('kind', models.CharField(choices=[('orders', 'Pedidos'), ('financial', 'Financeiro'), ('catalog', 'Catálogo')], help_text='Tipo de sincronização', max_length=40)),
                ('started_at', models.DateTimeField(auto_now_add=True, help_text='Início da sincronização')),
                ('finished_at', models.DateTimeField(blank=True, help_text='Fim da sincronização', null=True)),
                ('ok', models.BooleanField(default=False, help_text='Sincronização bem-sucedida')),
                ('items_ingested', models.IntegerField(default=0, help_text='Quantidade de itens processados/inseridos')),
                ('error', models.TextField(blank=True, help_text='Mensagem de erro (se houver)', null=True)),
                ('metadata', models.JSONField(blank=True, default=dict, help_text='Metadados adicionais da sincronização (JSON)')),
                ('store', models.ForeignKey(help_text='Loja sincronizada', on_delete=django.db.models.deletion.CASCADE, related_name='sync_runs', to='app_ifood_integration.ifoodstore')),
            ],
            options={
                'verbose_name': 'Execução de Sincronização',
                'verbose_name_plural': 'Execuções de Sincronização',
                'db_table': 'ifood_sync_run',
                'ordering': ['-started_at'],
            },
        ),
        migrations.AddIndex(
            model_name='ifoodsyncrun',
            index=models.Index(fields=['store', 'kind', '-started_at'], name='ifood_sync_store_k_idx'),
        ),
        migrations.AddIndex(
            model_name='ifoodsyncrun',
            index=models.Index(fields=['ok', '-started_at'], name='ifood_sync_ok_start_idx'),
        ),
        migrations.CreateModel(
            name='MrfooPayout',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('payout_id', models.CharField(db_index=True, help_text='ID único do repasse no iFood', max_length=100, unique=True)),
                ('reference_period', models.CharField(help_text="Período de referência (ex: '2024-01')", max_length=20)),
                ('gross', models.DecimalField(decimal_places=2, help_text='Valor bruto', max_digits=10)),
                ('fees', models.DecimalField(decimal_places=2, default=0, help_text='Taxas descontadas', max_digits=10)),
                ('net', models.DecimalField(decimal_places=2, help_text='Valor líquido (bruto - taxas)', max_digits=10)),
                ('channel', models.CharField(default='ifood', help_text='Canal de origem', max_length=20)),
                ('raw_json', models.JSONField(blank=True, default=dict, help_text='Dados brutos do repasse (JSON completo do iFood)')),
                ('synced_at', models.DateTimeField(auto_now_add=True, help_text='Data/hora da sincronização')),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('store', models.ForeignKey(help_text='Loja que recebeu o repasse', on_delete=django.db.models.deletion.CASCADE, related_name='payouts', to='app_ifood_integration.ifoodstore')),
            ],
            options={
                'verbose_name': 'Repasse MrFoo',
                'verbose_name_plural': 'Repasses MrFoo',
                'db_table': 'mrfoo_payout',
                'ordering': ['-reference_period', 'store'],
            },
        ),
        migrations.CreateModel(
            name='MrfooOrder',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('order_id', models.CharField(db_index=True, help_text='ID único do pedido no iFood', max_length=100, unique=True)),
                ('created_at', models.DateTimeField(help_text='Data/hora de criação do pedido')),
                ('status', models.CharField(choices=[('PENDING', 'Pendente'), ('CONFIRMED', 'Confirmado'), ('PREPARING', 'Preparando'), ('READY', 'Pronto'), ('DISPATCHED', 'Despachado'), ('DELIVERED', 'Entregue'), ('CANCELLED', 'Cancelado')], default='PENDING', help_text='Status atual do pedido', max_length=20)),
                ('total_value', models.DecimalField(decimal_places=2, help_text='Valor total do pedido', max_digits=10)),
                ('channel', models.CharField(default='ifood', help_text='Canal de origem (ifood, delivery, etc.)', max_length=20)),
                ('raw_json', models.JSONField(blank=True, default=dict, help_text='Dados brutos do pedido (JSON completo do iFood)')),
                ('synced_at', models.DateTimeField(auto_now_add=True, help_text='Data/hora da sincronização')),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('store', models.ForeignKey(help_text='Loja que recebeu o pedido', on_delete=django.db.models.deletion.CASCADE, related_name='orders', to='app_ifood_integration.ifoodstore')),
            ],
            options={
                'verbose_name': 'Pedido MrFoo',
                'verbose_name_plural': 'Pedidos MrFoo',
                'db_table': 'mrfoo_order',
                'ordering': ['-created_at'],
            },
        ),
        migrations.AddIndex(
            model_name='mrfoopayout',
            index=models.Index(fields=['store', '-reference_period'], name='mrfoo_pay_store_ref_idx'),
        ),
        migrations.AddIndex(
            model_name='mrfoopayout',
            index=models.Index(fields=['channel', '-reference_period'], name='mrfoo_pay_chan_ref_idx'),
        ),
        migrations.AddIndex(
            model_name='mrfooorder',
            index=models.Index(fields=['store', '-created_at'], name='mrfoo_ord_store_cre_idx'),
        ),
        migrations.AddIndex(
            model_name='mrfooorder',
            index=models.Index(fields=['status', '-created_at'], name='mrfoo_ord_status_cr_idx'),
        ),
        migrations.AddIndex(
            model_name='mrfooorder',
            index=models.Index(fields=['channel', '-created_at'], name='mrfoo_ord_chan_cre_idx'),
        ),
    ]

