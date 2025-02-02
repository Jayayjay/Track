from django.shortcuts import render
from athlete_records.views import AthleteList

def homepage(request):
    return render(request, 'index.html')

def about(request):
    return render(request, 'about-us.html')

def coaches(request):
    return render(request, 'coaches.html')

def season_schedule(request):
    return render(request, 'season-timetable.html')

def record_view(request):
    return render(request, AthleteList)

def registeration_view(request):
    return render(request, 'registeration.html')

def not_found(request):
    return render(request, '404.html')