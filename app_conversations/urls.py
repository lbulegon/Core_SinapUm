# ============================================================================
# ARQUITETURA NOVA - app_conversations.urls
# ============================================================================

from django.urls import path
from . import views

app_name = 'app_conversations'

urlpatterns = [
    # Listar conversas
    path(
        'console/conversations',
        views.list_conversations,
        name='list_conversations'
    ),
    
    # Detalhe de conversa
    path(
        'console/conversations/<str:conversation_id>',
        views.get_conversation,
        name='get_conversation'
    ),
    
    # Sugestões
    path(
        'console/conversations/<str:conversation_id>/suggestions',
        views.get_suggestions,
        name='get_suggestions'
    ),
    
    # Enviar sugestão
    path(
        'console/suggestions/<str:suggestion_id>/send',
        views.send_suggestion,
        name='send_suggestion'
    ),
    
    # Enviar mensagem manual
    path(
        'console/messages/send',
        views.send_message,
        name='send_message'
    ),
]

