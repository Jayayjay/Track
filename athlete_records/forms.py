from django import forms
from .models import AthleteRecords

class AthleteRecordsForms(forms.ModelForm):
    class Meta:
        model = AthleteRecords
        fields = ['athlete_class','athlete_name', 'athlete_mark', 'athlete_age', 'athlete_group', 'athlete_date', 'athlete_meet']
        