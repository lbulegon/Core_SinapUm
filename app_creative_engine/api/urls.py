"""
URLs da API do Creative Engine
"""
from django.urls import path
from app_creative_engine.api import views
from app_creative_engine import views as main_views

app_name = 'creative_engine'

urlpatterns = [
    path('generate', views.generate_creative, name='generate'),
    path('<str:creative_id>/variants', views.generate_variants, name='generate_variants'),
    path('variants/<str:variant_id>/adapt', views.adapt_creative, name='adapt'),
    path('performance', views.register_performance, name='performance'),
    path('recommend', views.recommend_next, name='recommend'),
    # Jobs (fluxo Kwai/Tamo)
    path('jobs/', views.create_job, name='create_job'),
    path('jobs/<uuid:job_id>/', views.job_status, name='job_status'),
    path('jobs/<uuid:job_id>/outputs/', views.job_outputs, name='job_outputs'),
    path('list/', main_views.list_creatives, name='list'),
    path('test/', main_views.test_creative_engine, name='test'),
    # Markdown -> PDF
    path('md-to-pdf/', views.generate_pdf_from_markdown, name='md_to_pdf'),
    # Geração de imagens por IA (descrição e/ou imagem modelo)
    path('image-from-prompt/', views.generate_image_from_prompt, name='generate_image_from_prompt'),
    # Geração de vídeos por IA (Sora)
    path('video-from-prompt/', views.generate_video_from_prompt, name='generate_video_from_prompt'),
    # Geração de áudio por IA (texto → fala / TTS)
    path('audio-from-text/', views.generate_audio_from_text, name='generate_audio_from_text'),
]
