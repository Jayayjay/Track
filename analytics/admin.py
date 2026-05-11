from django.contrib import admin
from .models import AnalyticsSnapshot

@admin.register(AnalyticsSnapshot)
class AnalyticsSnapshotAdmin(admin.ModelAdmin):
    list_display = ['date', 'metric_name', 'dimension', 'value']
    list_filter = ['metric_name']
    date_hierarchy = 'date'
