from django.shortcuts import render

def homepage(request):
    return render(request, 'index.html')

def about(request):
    return render(request, 'about-us.html')

def coaches(request):
    return render(request, 'coaches.html')

def season_schedule(request):
    return render(request, 'season-timetable.html')