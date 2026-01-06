"""
URLs do WhatsApp Gateway
"""
from django.urls import path
from app_whatsapp.api import views

app_name = 'whatsapp'

urlpatterns = [
    path('instances/', views.create_instance, name='create_instance'),
    path('instances/<str:instance_key>/qr/', views.get_qr, name='get_qr'),
    path('instances/<str:instance_key>/simulate/scan/', views.simulate_scan, name='simulate_scan'),
    path('instances/<str:instance_key>/simulate/disconnect/', views.simulate_disconnect, name='simulate_disconnect'),
    path('instances/<str:instance_key>/simulate/inbound/', views.simulate_inbound, name='simulate_inbound'),
    path('send/', views.send_message, name='send_message'),
    path('inbound/', views.inbound_webhook, name='inbound_webhook'),
    path('health/', views.health, name='health'),
]
