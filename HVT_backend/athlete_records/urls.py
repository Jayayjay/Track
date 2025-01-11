from django.urls import path
from .views import AthleteList

urlpatterns = [
    path('api/athlete_list', AthleteList.as_view(), name='athlete_record')
]
