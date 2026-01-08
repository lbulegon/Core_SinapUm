"""
Admin - WhatsApp Gateway
"""
from django.contrib import admin
from django.apps import apps

# Registrar SimulatedMessage se modelo estiver disponível
try:
    SimulatedMessage = apps.get_model('core.services.whatsapp', 'SimulatedMessage')
    
    @admin.register(SimulatedMessage)
    class SimulatedMessageAdmin(admin.ModelAdmin):
        """Admin para SimulatedMessage"""
        list_display = ['to', 'message_type', 'created_at', 'text_preview']
        list_filter = ['message_type', 'created_at']
        search_fields = ['to', 'text']
        readonly_fields = ['id', 'created_at']
        
        def text_preview(self, obj):
            """Preview do texto"""
            if obj.text:
                return obj.text[:50] + '...' if len(obj.text) > 50 else obj.text
            return '-'
        text_preview.short_description = 'Texto'
except LookupError:
    # Model não está disponível (app não instalado ou migration não aplicada)
    pass
