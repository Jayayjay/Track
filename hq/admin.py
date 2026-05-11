from django.contrib import admin
from .models import SeasonProgram, HQRegistration


@admin.register(SeasonProgram)
class SeasonProgramAdmin(admin.ModelAdmin):
    list_display  = ['name', 'season', 'fee', 'early_bird_fee', 'registration_open', 'registration_close', 'is_active']
    list_editable = ['is_active']


@admin.register(HQRegistration)
class HQRegistrationAdmin(admin.ModelAdmin):
    list_display  = ['athlete_first_name', 'athlete_last_name', 'program', 'user', 'status', 'created_at']
    list_filter   = ['status', 'program']
    search_fields = ['athlete_first_name', 'athlete_last_name', 'user__email']
    readonly_fields = ['created_at']
