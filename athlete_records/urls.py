from django.urls import path
from .views import (
    AthleteList,
    CreateAthlete,
)
app_name ="athlete_records"
urlpatterns = [

    path('', AthleteList.as_view(), name='record_list'), # '/api/athlete_records/list/'
    path('add/', CreateAthlete.as_view(), name='add-athlete'),
]
