from rest_framework import serializers
from .models import AthleteRecords

class AthleteSerializer(serializers.ModelSerializer):
    class Meta:
        model = AthleteRecords
        fields = '__all__'