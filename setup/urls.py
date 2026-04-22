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
from django.urls import path, include
from django.conf import settings
from django.views.generic import RedirectView
from django.conf.urls.static import static
from app_sinapum import views
from app_sinapum import views_core
from app_sinapum import views_environmental_state
from app_sinapum import environmental_views
from app_sinapum import views_baileys
from app_sinapcore import eoc_views
from core.services.whatsapp import webhook_handler

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
    path('rag-gastronomico/api/start/', views.rag_gastronomico_ingest_start, name='rag_gastronomico_ingest_start'),
    path(
        'rag-gastronomico/api/status/<uuid:job_id>/',
        views.rag_gastronomico_ingest_status,
        name='rag_gastronomico_ingest_status',
    ),
    path('rag-gastronomico/api/preview/', views.rag_gastronomico_preview, name='rag_gastronomico_preview'),
    path('rag-gastronomico/api/commit/', views.rag_gastronomico_commit, name='rag_gastronomico_commit'),
    path('rag-gastronomico/', views.rag_gastronomico, name='rag_gastronomico'),
    path('analyze/', views.analyze_image, name='analyze_image'),
    path('analyze/save-product/', views.save_product_json, name='save_product_json'),
    path('analyze/add-images-ajax/', views.handle_add_images_ajax, name='add_images_ajax'),
    path('analyze/reanalyze-ajax/', views.handle_reanalyze, name='reanalyze_ajax'),
    # API REST endpoint para análise de imagens (usado pelo Évora)
    path('api/v1/analyze-product-image', views.api_analyze_product_image, name='api_analyze_product_image'),
    # Core Registry endpoints (MCP) - Novo app_mcp_tool_registry
    path('core/', include('app_mcp_tool_registry.urls')),
    # ACP — Agent Communication Protocol (tarefas de agente)
    path('acp/', include('app_acp.urls')),
    # A2A — Agent to Agent (Planner + Executor)
    path('a2a/', include('a2a.urls')),
    # Integração iFood (API interna)
    path('', include('app_ifood_integration.urls')),
    # Lead Registry - Sistema central de captação de leads
    path('', include('app_leads.urls')),
    # Estado ambiental (Redis) — Mapa de Estado Ambiental / orbital environmental_indiciary
    path(
        'api/v1/environment/<int:estabelecimento_id>/',
        views_environmental_state.get_environmental_state,
        name='api_environmental_state',
    ),
    path(
        'environmental/',
        RedirectView.as_view(url='/environmental/1/', permanent=False),
        name='environmental_dashboard_redirect',
    ),
    path(
        'environmental/<int:estabelecimento_id>/',
        environmental_views.environmental_dashboard,
        name='environmental_dashboard',
    ),
    # Health check (mantido para compatibilidade)
    path('health', views_core.health_check, name='health_check'),
    # WhatsApp - Usa Baileys (whatsapp_gateway_service) - Evolution API removida
    path('whatsapp/', views_baileys.whatsapp_gateway_connect, name='whatsapp_connect'),
    # WhatsApp Gateway Service (Baileys) - endpoints detalhados
    path('whatsapp/gateway/', views_baileys.whatsapp_gateway_connect, name='whatsapp_gateway_connect'),
    path('whatsapp/gateway/connect/', views_baileys.whatsapp_gateway_connect_action, name='whatsapp_gateway_connect_action'),
    path('whatsapp/gateway/qr/', views_baileys.whatsapp_gateway_get_qr, name='whatsapp_gateway_get_qr'),
    path('whatsapp/gateway/status/', views_baileys.whatsapp_gateway_get_status, name='whatsapp_gateway_get_status'),
    path('whatsapp/gateway/disconnect/', views_baileys.whatsapp_gateway_disconnect, name='whatsapp_gateway_disconnect'),
    path('whatsapp/gateway/reset/', views_baileys.whatsapp_gateway_reset_session, name='whatsapp_gateway_reset_session'),
    # Proxy transparente Baileys - permite ao Évora usar porta Django (5000) em vez da 8007
    path('whatsapp/proxy/<path:endpoint>', views_baileys.whatsapp_baileys_proxy, name='whatsapp_baileys_proxy'),
    # WhatsApp Gateway - Nova arquitetura plugável
    path('api/whatsapp/', include('app_whatsapp.api.urls')),
    # Creative Engine - Motor de criativos
    path('api/creative-engine/', include('app_creative_engine.api.urls')),
    # Architecture Intelligence - Avaliação arquitetural
    path('architecture/', include('app_architecture_intelligence.urls')),
    # Agent Core (PAOR) — integração com governança arquitetural
    path('agent-core/', include('agent_core.urls')),
    # SinapCore — dashboard módulos + logs de auditoria (staff)
    path('sinapcore/', include('app_sinapcore.urls')),
    # MrFoo Agno — exposição read-only (KDS/apps) — protegida por segredo + feature flags
    path('agno/', include('app_sinapcore.agno_urls')),
    # SinapLint Cloud (API key por tenant) — análise arquitetural
    path('api/sinaplint/', include('app_sinapcore.api_urls')),
    # SinapLint SaaS — utilizador Django, Stripe, limites mensais
    path('api/sinaplint/saas/', include('app_sinaplint.urls_saas')),
    # EOC — Centro de Operações Cognitivo (torre SinapCore + ambiente + logs)
    path('eoc/', eoc_views.eoc_dashboard, name='eoc_dashboard'),
    path('eoc/<int:estabelecimento_id>/', eoc_views.eoc_dashboard, name='eoc_dashboard_establishment'),
    path('eoc/command/', eoc_views.eoc_send_command, name='eoc_send_command'),
    # ============================================================================
    # WhatsApp Canonical Events v1.0
    # ============================================================================
    path('api/v1/whatsapp/events/', include('core.services.whatsapp.canonical.urls')),
    # WhatsApp Gateway Service Webhook
    path('webhooks/whatsapp/', webhook_handler.handle_incoming_whatsapp_event, name='whatsapp_gateway_webhook'),
    path('admin/', admin.site.urls),
]

# ============================================================================
# ARQUITETURA NOVA - WhatsApp Gateway Multi-tenant
# ============================================================================
# URLs da nova arquitetura (com feature flags)
# ANTIGO: /whatsapp/api/* e /api/whatsapp/* (mantidos acima)
# NOVO: /webhooks/evolution/*, /console/*, /ai/*, /mcp/*
# ============================================================================

# Feature flags (verificar se estão habilitadas)
FEATURE_EVOLUTION_MULTI_TENANT = getattr(settings, 'FEATURE_EVOLUTION_MULTI_TENANT', False)

if FEATURE_EVOLUTION_MULTI_TENANT:
    # Gateway WhatsApp
    urlpatterns += [
        path('', include('app_whatsapp_gateway.urls')),
    ]
    
    # Console de Conversas
    urlpatterns += [
        path('', include('app_conversations.urls')),
    ]
    
    # AI Bridge (se habilitado)
    FEATURE_OPENMIND_ENABLED = getattr(settings, 'FEATURE_OPENMIND_ENABLED', False)
    if FEATURE_OPENMIND_ENABLED:
        urlpatterns += [
            path('ai/', include('app_ai_bridge.urls')),
        ]
    
    # MCP Tools (se habilitado)
    urlpatterns += [
        path('mcp/', include('app_mcp.urls')),
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
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
