from django.contrib import admin
from .models import Athlete, Guardian, EmergencyContact, AthleteDocument

@admin.register(Athlete)
class AthleteAdmin(admin.ModelAdmin):
    list_display = ['last_name', 'first_name', 'team', 'status', 'date_of_birth', 'registration_date']
    list_filter = ['status', 'gender', 'team']
    search_fields = ['first_name', 'last_name', 'sportsengine_id']

@admin.register(Guardian)
class GuardianAdmin(admin.ModelAdmin):
    list_display = ['full_name', 'athlete', 'cell_phone', 'email', 'order']
    search_fields = ['first_name', 'last_name', 'email']

@admin.register(EmergencyContact)
class EmergencyContactAdmin(admin.ModelAdmin):
    list_display = ['full_name', 'athlete', 'relationship', 'home_phone']

@admin.register(AthleteDocument)
class AthleteDocumentAdmin(admin.ModelAdmin):
    list_display = ['athlete', 'document_type', 'is_verified', 'uploaded_at']
    list_filter = ['document_type', 'is_verified']
