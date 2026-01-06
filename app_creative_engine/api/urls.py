"""
URLs da API do Creative Engine
"""
from django.urls import path
from app_creative_engine.api import views

app_name = 'creative_engine'

urlpatterns = [
    path('generate', views.generate_creative, name='generate'),
    path('<str:creative_id>/variants', views.generate_variants, name='generate_variants'),
    path('variants/<str:variant_id>/adapt', views.adapt_creative, name='adapt'),
    path('performance', views.register_performance, name='performance'),
    path('recommend', views.recommend_next, name='recommend'),
]
