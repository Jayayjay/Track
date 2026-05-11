from django.contrib import admin
from .models import Team, PracticeAttendance, TrainingSession, TransferRequest

@admin.register(Team)
class TeamAdmin(admin.ModelAdmin):
    list_display = ['name', 'age_group', 'season', 'head_coach', 'status', 'current_athletes', 'max_athletes']
    list_filter = ['status', 'age_group', 'season']
    search_fields = ['name']

@admin.register(PracticeAttendance)
class PracticeAttendanceAdmin(admin.ModelAdmin):
    list_display = ['athlete', 'team', 'practice_date', 'attended']
    list_filter = ['attended', 'team']

@admin.register(TrainingSession)
class TrainingSessionAdmin(admin.ModelAdmin):
    list_display = ['title', 'team', 'session_type', 'start_datetime', 'location']
    list_filter = ['session_type', 'team', 'recurrence']

@admin.register(TransferRequest)
class TransferRequestAdmin(admin.ModelAdmin):
    list_display = ['athlete', 'from_team', 'to_team', 'status', 'created_at']
    list_filter = ['status']
