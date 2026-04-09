from django.contrib import admin
from .models import ArchitectureCycle, ArchitectureStageRun, ArchitectureDecisionLog, ArchitectureRisk


@admin.register(ArchitectureCycle)
class ArchitectureCycleAdmin(admin.ModelAdmin):
    list_display = ("id", "cycle_type", "state", "trace_id", "created_at")
    search_fields = ("id", "trace_id")


@admin.register(ArchitectureStageRun)
class ArchitectureStageRunAdmin(admin.ModelAdmin):
    list_display = ("id", "cycle_id", "stage", "state", "created_at")
    list_filter = ("stage", "state")


@admin.register(ArchitectureDecisionLog)
class ArchitectureDecisionLogAdmin(admin.ModelAdmin):
    list_display = ("id", "cycle_id", "stage", "created_at")


@admin.register(ArchitectureRisk)
class ArchitectureRiskAdmin(admin.ModelAdmin):
    list_display = ("id", "cycle_id", "stage", "severity", "created_at")
