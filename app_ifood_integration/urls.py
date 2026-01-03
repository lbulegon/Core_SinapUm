"""
URLs para app_ifood_integration (API interna)
"""
from django.urls import path
from . import views

app_name = 'ifood_integration'

urlpatterns = [
    # Endpoints de lojas
    path('internal/ifood/stores', views.list_stores, name='list_stores'),
    path('internal/ifood/stores/<int:store_id>/status', views.store_status, name='store_status'),
    path('internal/ifood/stores/<int:store_id>/tokens', views.save_oauth_tokens, name='save_oauth_tokens'),
    path('internal/ifood/stores/<int:store_id>/sync/orders', views.sync_orders, name='sync_orders'),
    path('internal/ifood/stores/<int:store_id>/sync/finance', views.sync_finance, name='sync_finance'),
    
    # Endpoints de sincronização
    path('internal/ifood/stores/<int:store_id>/sync-runs', views.create_sync_run, name='create_sync_run'),
    path('internal/ifood/sync-runs/<int:sync_run_id>', views.update_sync_run, name='update_sync_run'),
    
    # Endpoints de dados normalizados (MrFoo)
    path('internal/mrfoo/orders', views.list_orders, name='list_orders'),
    path('internal/mrfoo/orders/save', views.save_order, name='save_order'),
    path('internal/mrfoo/payouts', views.list_payouts, name='list_payouts'),
    path('internal/mrfoo/payouts/save', views.save_payout, name='save_payout'),
]

