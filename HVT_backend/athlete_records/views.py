from django.shortcuts import render, redirect
from athlete_records.models import AthleteRecords
from .forms import AthleteRecordsForms

# Create your views here.
def record_view(request):
    athlete_records = AthleteRecords.objects.all()
    context = {'athlete_records': athlete_records}
    return render(request, 'templates/records/record.html')
#     return render(request, 'record/records.html')

# def new_record_view(request):
#     if request.method == "POST":
#         form = AthleteRecordsForms(request.POST)
#         if form.is_valid():
#             form.save()
    
#     return redirect('')