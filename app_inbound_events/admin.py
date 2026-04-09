from django.contrib import admin
from .models import DecisionLog, InboundEvent


@admin.register(InboundEvent)
class InboundEventAdmin(admin.ModelAdmin):
    list_display = ("event_id", "source", "status", "received_at", "processed_at")
    list_filter = ("source", "status")
    search_fields = ("event_id",)
    readonly_fields = ("id", "received_at", "processed_at")


@admin.register(DecisionLog)
class DecisionLogAdmin(admin.ModelAdmin):
    list_display = ("event_id", "source", "recorded_at")
    list_filter = ("source",)
    search_fields = ("event_id",)
    readonly_fields = ("id", "recorded_at")
