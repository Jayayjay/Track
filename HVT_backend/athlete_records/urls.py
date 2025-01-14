from django.urls import path
from .views import (
    AthleteList,
    
)

urlpatterns = [

    path('list/', AthleteList.as_view(), name='athlete_record'), # '/api/athlete_records/list/'
    # path('add/', CreateAthlete.as_view(), name='add-athlete'),
]
