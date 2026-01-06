"""
Admin do Creative Engine
"""
from django.contrib import admin
from app_creative_engine.models import CreativeAsset, CreativePerformance, CreativeScore


@admin.register(CreativeAsset)
class CreativeAssetAdmin(admin.ModelAdmin):
    """Admin para assets de criativo"""
    list_display = ['creative_id', 'variant_id', 'product_id', 'channel', 'strategy', 'created_at']
    list_filter = ['channel', 'strategy', 'created_at']
    search_fields = ['creative_id', 'variant_id', 'product_id', 'shopper_id']
    readonly_fields = ['id', 'created_at', 'updated_at']
    date_hierarchy = 'created_at'


@admin.register(CreativePerformance)
class CreativePerformanceAdmin(admin.ModelAdmin):
    """Admin para performance de criativos"""
    list_display = ['variant_id', 'event_type', 'product_id', 'created_at']
    list_filter = ['event_type', 'created_at']
    search_fields = ['variant_id', 'creative_id', 'product_id', 'shopper_id']
    readonly_fields = ['id', 'created_at']
    date_hierarchy = 'created_at'


@admin.register(CreativeScore)
class CreativeScoreAdmin(admin.ModelAdmin):
    """Admin para scores de criativos"""
    list_display = ['variant_id', 'strategy', 'channel', 'engagement_score', 'total_views', 'calculated_at']
    list_filter = ['strategy', 'channel', 'calculated_at']
    search_fields = ['variant_id', 'creative_id', 'product_id']
    readonly_fields = ['calculated_at']
    ordering = ['-engagement_score']
