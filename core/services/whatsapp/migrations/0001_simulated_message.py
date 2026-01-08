# Generated migration - SimulatedMessage

from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='SimulatedMessage',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('to', models.CharField(db_index=True, max_length=20)),
                ('text', models.TextField(blank=True)),
                ('media_url', models.URLField(blank=True, null=True)),
                ('caption', models.TextField(blank=True)),
                ('message_type', models.CharField(default='text', max_length=20)),
                ('metadata', models.JSONField(blank=True, default=dict)),
                ('created_at', models.DateTimeField(auto_now_add=True, db_index=True)),
            ],
            options={
                'db_table': 'core_whatsapp_simulated_message',
                'ordering': ['-created_at'],
            },
        ),
        migrations.AddIndex(
            model_name='simulatedmessage',
            index=models.Index(fields=['to', '-created_at'], name='core_whatsap_to_creat_idx'),
        ),
    ]
