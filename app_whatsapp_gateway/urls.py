# ============================================================================
# ARQUITETURA NOVA - app_whatsapp_gateway.urls
# ============================================================================

from django.urls import path
from . import views

app_name = 'app_whatsapp_gateway'

urlpatterns = [
    # Webhooks
    path(
        'webhooks/evolution/<str:instance_id>/messages',
        views.webhook_receiver,
        name='webhook_receiver'
    ),
    
    # Instâncias
    path(
        'instances/evolution/create',
        views.create_instance,
        name='create_instance'
    ),
    path(
        'instances/evolution/<str:instance_id>/qr',
        views.get_qr,
        name='get_qr'
    ),
    path(
        'instances/evolution/<str:instance_id>/connect',
        views.connect,
        name='connect'
    ),
    
    # Enviar mensagens
    path(
        'channels/whatsapp/send',
        views.send_message,
        name='send_message'
    ),
]

