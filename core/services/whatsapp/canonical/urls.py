"""
URLs - WhatsApp Canonical Events v1.0
"""
from django.urls import path
from . import views

app_name = 'canonical_events'

urlpatterns = [
    path('inbound', views.inbound_event, name='inbound_event'),
    path('status', views.status_event, name='status_event'),
    path('health', views.health_check, name='health_check'),
]
