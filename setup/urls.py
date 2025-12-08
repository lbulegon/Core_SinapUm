"""
URL configuration for setup project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from app_sinapum import views

# Importar views do CrewAI (com try/except para não quebrar se CrewAI não estiver instalado)
try:
    from app_sinapum import views_crewai as crewai_views
    CREWAI_AVAILABLE = True
except ImportError:
    CREWAI_AVAILABLE = False
    crewai_views = None

# Importar views do Agnos (com try/except para não quebrar se Agnos não estiver instalado)
try:
    from app_sinapum import views_agnos as agnos_views
    AGNOS_AVAILABLE = True
except ImportError:
    AGNOS_AVAILABLE = False
    agnos_views = None

urlpatterns = [
    path('', views.home, name='home'),
    path('analyze/', views.analyze_image, name='analyze_image'),
    path('analyze/save-product/', views.save_product_json, name='save_product_json'),
    path('analyze/add-images-ajax/', views.handle_add_images_ajax, name='add_images_ajax'),
    path('analyze/reanalyze-ajax/', views.handle_reanalyze, name='reanalyze_ajax'),
    # API REST endpoint para análise de imagens (usado pelo Évora)
    path('api/v1/analyze-product-image', views.api_analyze_product_image, name='api_analyze_product_image'),
    path('admin/', admin.site.urls),
]

# Adicionar rotas do CrewAI se disponível
if CREWAI_AVAILABLE and crewai_views:
    urlpatterns += [
        path('analyze/crewai/', crewai_views.analyze_with_crewai, name='analyze_crewai'),
        path('api/crewai/analyze/', crewai_views.api_analyze_crewai, name='api_crewai_analyze'),
    ]

# Adicionar rotas do Agnos se disponível
if AGNOS_AVAILABLE and agnos_views:
    urlpatterns += [
        path('analyze/agnos/', agnos_views.analyze_with_agnos, name='analyze_agnos'),
        path('api/agnos/analyze/', agnos_views.api_analyze_agnos, name='api_agnos_analyze'),
        path('api/agnos/validate/', agnos_views.api_validate_agnos, name='api_agnos_validate'),
    ]

# Servir arquivos de mídia (necessário para servir imagens salvas)
# Em produção, considere usar nginx ou outro servidor web para servir arquivos estáticos
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
