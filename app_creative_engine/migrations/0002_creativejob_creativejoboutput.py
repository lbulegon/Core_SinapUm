# Generated manually for Creative Engine Jobs (fluxo Kwai/Tamo)

from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('app_creative_engine', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='CreativeJob',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('shopper_id', models.CharField(blank=True, db_index=True, max_length=128, null=True)),
                ('product_id', models.CharField(blank=True, db_index=True, max_length=128, null=True)),
                ('image_path', models.CharField(help_text='Caminho da imagem de entrada', max_length=512)),
                ('image_url', models.URLField(blank=True, help_text='URL da imagem (alternativa)', null=True)),
                ('status', models.CharField(choices=[('queued', 'Na fila'), ('processing', 'Processando'), ('completed', 'Concluído'), ('failed', 'Falhou')], db_index=True, default='queued', max_length=20)),
                ('stage', models.CharField(blank=True, help_text='Etapa atual: analyzing, removing_bg, generating', max_length=64)),
                ('progress', models.IntegerField(default=0, help_text='0-100')),
                ('description', models.TextField(blank=True, help_text='Descrição gerada do produto')),
                ('error_message', models.TextField(blank=True, null=True)),
                ('metadata', models.JSONField(blank=True, default=dict)),
                ('created_at', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('completed_at', models.DateTimeField(blank=True, null=True)),
            ],
            options={
                'db_table': 'creative_job',
                'ordering': ['-created_at'],
            },
        ),
        migrations.CreateModel(
            name='CreativeJobOutput',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('style', models.CharField(db_index=True, max_length=64)),
                ('template_id', models.CharField(blank=True, max_length=64)),
                ('image_url', models.URLField()),
                ('thumbnail_url', models.URLField(blank=True, null=True)),
                ('metadata', models.JSONField(blank=True, default=dict)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('job', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='outputs', to='app_creative_engine.creativejob')),
            ],
            options={
                'db_table': 'creative_job_output',
                'ordering': ['created_at'],
            },
        ),
    ]
