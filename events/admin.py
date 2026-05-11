from django.contrib import admin
from .models import Event, EventRegistration

@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ['name', 'event_type', 'start_datetime', 'venue_name', 'is_published', 'is_cancelled']
    list_filter = ['event_type', 'is_published', 'is_cancelled']
    search_fields = ['name', 'venue_name']

@admin.register(EventRegistration)
class EventRegistrationAdmin(admin.ModelAdmin):
    list_display = ['event', 'athlete', 'status', 'payment_received', 'registered_at']
    list_filter = ['status', 'payment_received']
