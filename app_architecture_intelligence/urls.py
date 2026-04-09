"""
URLs do Architecture Intelligence
"""
from django.urls import path
from . import views

app_name = "architecture_intelligence"

urlpatterns = [
    path("", views.dashboard, name="dashboard"),
    path("evaluate", views.evaluate, name="evaluate"),
]
