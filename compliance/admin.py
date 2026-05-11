from django.contrib import admin
from .models import ComplianceRecord, BackgroundCheck, IncidentReport, AuditLog

@admin.register(ComplianceRecord)
class ComplianceRecordAdmin(admin.ModelAdmin):
    list_display = ['user', 'athlete', 'record_type', 'status', 'expiry_date', 'verified_by']
    list_filter = ['status', 'record_type']

@admin.register(BackgroundCheck)
class BackgroundCheckAdmin(admin.ModelAdmin):
    list_display = ['user', 'provider', 'status', 'submitted_date', 'expiry_date']
    list_filter = ['status']

@admin.register(IncidentReport)
class IncidentReportAdmin(admin.ModelAdmin):
    list_display = ['title', 'incident_type', 'severity', 'status', 'incident_date', 'reported_by']
    list_filter = ['severity', 'status', 'incident_type']

@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ['user', 'action', 'model_name', 'object_repr', 'timestamp']
    list_filter = ['action', 'model_name']
    readonly_fields = ['user', 'action', 'model_name', 'object_id', 'object_repr', 'changes', 'ip_address', 'timestamp']
