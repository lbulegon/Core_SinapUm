"""
URLs do Lead Registry.
"""
from django.urls import path
from .views import capture_lead

app_name = "app_leads"

urlpatterns = [
    path("api/leads/capture", capture_lead, name="capture_lead"),
]

