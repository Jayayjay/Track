from django.contrib import admin
from django.urls import path, include
from . import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('index/', views.homepage, name='index'),
    path('about/', views.about, name='about'),
    path('season_schedule/', views.season_schedule, name='schedule'),
    path('coaches/', views.coaches, name='coaches'),
    path('contact/', include('contact.urls')),
    path('api/athlete_records/', include('athlete_records.urls') )
    
]
