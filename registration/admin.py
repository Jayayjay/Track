from django.contrib import admin
from .models import RegistrationFormConfig, RegistrationSubmission, RegistrationOrder, Waiver, BulkImportLog

@admin.register(RegistrationFormConfig)
class RegistrationFormConfigAdmin(admin.ModelAdmin):
    list_display = ['season', 'field_name', 'field_label', 'field_type', 'is_required', 'is_enabled', 'order']
    list_filter = ['season', 'is_required', 'is_enabled']

@admin.register(RegistrationSubmission)
class RegistrationSubmissionAdmin(admin.ModelAdmin):
    list_display = ['athlete', 'season', 'submitted_by', 'status', 'submitted_at']
    list_filter = ['status', 'season']

@admin.register(RegistrationOrder)
class RegistrationOrderAdmin(admin.ModelAdmin):
    list_display = ['athlete', 'season', 'order_number', 'order_status', 'registration_fee', 'registration_date']
    list_filter = ['order_status', 'season']
    search_fields = ['athlete__first_name', 'athlete__last_name', 'order_number']

@admin.register(Waiver)
class WaiverAdmin(admin.ModelAdmin):
    list_display = ['athlete', 'season', 'signed_by_name', 'signed_at']

@admin.register(BulkImportLog)
class BulkImportLogAdmin(admin.ModelAdmin):
    list_display = ['filename', 'import_type', 'total_records', 'successful_records', 'failed_records', 'uploaded_at']
