from django.contrib import admin
from .models import AthleteRecords

# Register your models here.
class AthleteRecordsAdmin (admin.ModelAdmin):
    list_display = [
        'athlete_name',
        'athlete_mark',
        'athlete_age',
        'athlete_group',
        'athlete_date',
        'athlete_meet'
    ]
admin.site.register(AthleteRecords, AthleteRecordsAdmin)